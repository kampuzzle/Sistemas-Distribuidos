import threading
import tensorflow as tf
import numpy as np
import grpc
import random
from concurrent import futures
import time

import federado_pb2
import federado_pb2_grpc

from model import define_model

import csv

# Definir os parâmetros do servidor
NUM_CLIENTS = 4 # Número de clientes a serem escolhidos em cada round
MIN_CLIENTS = 3 # Quantidade mínima de clientes participando em cada round
# MAX_ROUNDS = 5 # Quantidade máxima de rounds necessários para concluir o treinamento
MAX_ROUNDS = 20 # Quantidade máxima de rounds necessários para concluir o treinamento
TARGET_ACCURACY = 0.999 # Meta de acurácia
TIMEOUT = 100 # Timeout de conexão com os clientes em segundos
# Definir o modelo global usando Keras
global_model = define_model((28, 28, 1), 10)

# Compilar o modelo global com otimizador SGD e função de perda entropia cruzada categórica
global_model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

# Obter os pesos iniciais do modelo global
global_weights = global_model.get_weights()

client_weights = []

current_round = 0

round_data = {}

# Criar um dicionário para armazenar os clientes registrados
clients = {}

clients_history = []


def reshapeWeight(server_weight, weights):
    reshape_weight = []

    for layer_weights in weights:
        n_weights = np.prod(layer_weights.shape)
        reshape_weight.append(np.array(server_weight[:n_weights]).reshape(layer_weights.shape))
        server_weight = server_weight[n_weights:]

    return reshape_weight



# Criar uma classe para implementar o serviço de aprendizado federado definido no protobuf
class FederatedLearningServicer(federado_pb2_grpc.FederatedLearningServicer):

  # Registrar um cliente no servidor
  def RegisterClient(self, request, context):
    # Obter o ID, o IP e a porta do cliente da requisição
    client_id = request.client_id
    client_ip = request.client_ip
    client_port = request.client_port

    # Gerar um código de confirmação aleatório entre 0 e 9999
    confirmation_code = random.randint(0, 9999)

    # Armazenar o cliente no dicionário usando o ID como chave e o IP, a porta e o código como valores
    clients[client_id] = (client_ip, client_port, confirmation_code)

    # Imprimir uma mensagem informando que o cliente foi registrado
    print(f"Client {client_id} registered with IP {client_ip}, port {client_port} and confirmation code {confirmation_code}")

    # Retornar uma resposta com o código de confirmação e o número do round atual (inicialmente zero)
    return federado_pb2.RegisterClientResponse(confirmation_code=confirmation_code, current_round=0)



def choose_clients():
 
  # Criar uma lista com os IDs dos clientes registrados
  client_ids = list(clients.keys())

  # Embaralhar a lista de IDs
  random.shuffle(client_ids)

  # Obter os primeiros IDs da lista embaralhada
  chosen_clients = client_ids[:NUM_CLIENTS]

  # Imprimir uma mensagem informando os clientes escolhidos
  print(f"Choosen clients: {chosen_clients}")

  # Retornar os IDs dos clientes escolhidos
  return chosen_clients

def federated_average(weights, samples):
  # weights: a list of lists of weights from each client's model
  # samples: a list of the number of samples used for training by each client
  # returns: a list of weights that represent the weighted average of the local models
  
  # Initialize the average weights to zero
  avg_weights = [np.zeros_like(w) for w in weights[0]]
  
  # Sum up the weighted weights from each client
  for w, s in zip(weights, samples):
    avg_weights = [aw + s * cw for aw, cw in zip(avg_weights, w)]
  
  # Divide by the total number of samples
  avg_weights = [aw / sum(samples) for aw in avg_weights]
  
  return avg_weights

def train_client(client_id):
    client_ip, client_port, confirmation_code = clients[client_id]
    print(f"Training client {client_id}...")
    channel = grpc.insecure_channel(f"{client_ip}:{client_port}")
    stub = federado_pb2_grpc.ClientLearningStub(channel)
    try:
        response = stub.StartTraining(federado_pb2.StartTrainingRequest(current_round=current_round), timeout=TIMEOUT)
        client_weights.append((client_id,response.local_weights, response.local_samples))
    except grpc.RpcError as e:
        print(f"Error connecting to client {client_id}: {e}")
        #remove o cliente da lista de clientes
        clients.pop(client_id)
    print(f"Client {client_id} finished training.")

def evaluate_clients_thread(client_id, fedav_weights, round_number):
    global clients_history
    client_ip, client_port, confirmation_code = clients[client_id]
    print(f"Evaluating client {client_id}...")
    channel = grpc.insecure_channel(f"{client_ip}:{client_port}")
    stub = federado_pb2_grpc.ClientLearningStub(channel)
    try:
        response = stub.EvaluateModel(federado_pb2.EvaluateModelRequest(global_weights=fedav_weights), timeout=TIMEOUT)
        client_accuracy = response.accuracy
        print(f"Client {client_id} accuracy: {client_accuracy}")
        clients_history[round_number][client_id] = client_accuracy
        return client_accuracy
    except grpc.RpcError as e:
        print(f"Error connecting to client {client_id}: {e}")
        #remove o cliente da lista de clientes
        clients.pop(client_id)
        return 0.0


def test_global_model(fedav_weights): 

    x_test = np.load('teste/x_test.npy')
    y_test = np.load('teste/y_test.npy')

    # Test the global model
    global_model.set_weights(fedav_weights)
    _, accuracy = global_model.evaluate(x_test, y_test, verbose=0)
    print(f"Global model accuracy: {accuracy}")
    return accuracy

def train_clients_thread():
    global global_weights, current_round, clients_history
    i = 0
    clients_to_train = []
    while i < MAX_ROUNDS:
        # Se o número de clientes registrados for menor que o mínimo, aguardar 5 segundos e tentar novamente
        if len(clients) < MIN_CLIENTS:
            print("Currently connected clients:{}, need at least {}".format(len(clients), MIN_CLIENTS))
            time.sleep(2)
            continue
        else:
            clients_to_train = choose_clients()
            threads = []
            clients_history.append({})
       
            for client_id in clients_to_train:
                t = threading.Thread(target=train_client, args=(client_id,))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
        i += 1

        print("All chosen clients finished training.")
        ids, weights, samples = zip(*client_weights)
        fedav_weights = federated_average(weights, samples)
        


        reshaped_weights = reshapeWeight(fedav_weights,global_weights)
        accuracy = test_global_model(reshaped_weights)
        

        
        client_weights.clear()

        round_data[current_round] = {"round_id": current_round, "trainning_samples": sum(samples), "global_model_acc": accuracy, "clients": clients_to_train}
        
        #  Avaliando todos os clientes
        threads = []
        for client_id in clients:
            t = threading.Thread(target=evaluate_clients_thread, args=(client_id, fedav_weights, current_round))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        current_round += 1

        if accuracy >= TARGET_ACCURACY: 
            print("Accuracy target value was met at: " + str(accuracy) + " Finishing training...")
            break 


        print("All clients finished evaluation.")
    
    print("Training finished. Exiting...")

    # Salvando os pesos do modelo global em um arquivo
    global_model.save_weights('global_model_weights.h5')

    # Salvando os dados do round em um arquivo CSV
    with open('round_data.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["round_id", "trainning_samples", "global_model_acc", "clients"])
        writer.writeheader()
        for row in round_data.values():
            writer.writerow(row)
    print("Round data saved.")
   
    # Salvando os dados de treino de cada cliente em um arquivo CSV, cada cliente em um arquivo
    for i,round_info in enumerate(clients_history):
        for client_id, client_accuracy in round_info.items():
            with open(f'clients_history/client_{client_id}_history.csv', 'a') as f:
                writer = csv.DictWriter(f, fieldnames=["round_id", "accuracy"])
                writer.writerow({"round_id": i, "accuracy": client_accuracy})
        
    print("Client history saved.")
    return 


def serve():
    print("Starting server...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

    #  Thread para escolher os clientes a cada round
    threading.Thread(target=train_clients_thread).start()

    federado_pb2_grpc.add_FederatedLearningServicer_to_server(FederatedLearningServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Listening on port 8080.")
    server.wait_for_termination()

    

if __name__ == "__main__":
    serve()