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

# Definir os parâmetros do servidor
NUM_CLIENTS = 4 # Número de clientes a serem escolhidos em cada round
MIN_CLIENTS = 3 # Quantidade mínima de clientes participando em cada round
MAX_ROUNDS = 5 # Quantidade máxima de rounds necessários para concluir o treinamento
TARGET_ACCURACY = 0.9 # Meta de acurácia
TIMEOUT = 10 # Timeout de conexão com os clientes em segundos

# Definir o modelo global usando Keras
global_model = define_model((28, 28, 1), 10)

# Compilar o modelo global com otimizador SGD e função de perda entropia cruzada categórica
global_model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

# Obter os pesos iniciais do modelo global
global_weights = global_model.get_weights()



client_weights = []

current_round = 0

# Criar um dicionário para armazenar os clientes registrados
clients = {}

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

def federated_average(weights):
    # Initialize the average weights to zero
    avg_weights = [np.zeros_like(w) for w in weights[0]]
    # Sum up the weights from each client
    for w in weights:
        avg_weights = [aw + cw for aw, cw in zip(avg_weights, w)]
    # Divide by the number of clients
    avg_weights = [aw / len(weights) for aw in avg_weights]
    return avg_weights

def train_client(client_id):
    client_ip, client_port, confirmation_code = clients[client_id]
    print(f"Training client {client_id}...")
    channel = grpc.insecure_channel(f"{client_ip}:{client_port}")
    stub = federado_pb2_grpc.ClientLearningStub(channel)
    try:
        response = stub.StartTraining(federado_pb2.StartTrainingRequest(current_round=current_round), timeout=TIMEOUT)
        client_weights.append(response.local_weights)
    except grpc.RpcError as e:
        print(f"Error connecting to client {client_id}: {e}")
    print(f"Client {client_id} finished training.")

def evaluate_clients_thread(client_id, fedav_weights):
    client_ip, client_port, confirmation_code = clients[client_id]
    print(f"Evaluating client {client_id}...")
    channel = grpc.insecure_channel(f"{client_ip}:{client_port}")
    stub = federado_pb2_grpc.ClientLearningStub(channel)
    try:
        response = stub.EvaluateModel(federado_pb2.EvaluateModelRequest(global_weights=fedav_weights), timeout=TIMEOUT)
        client_accuracy = response.accuracy
        print(f"Client {client_id} accuracy: {client_accuracy}")
        return client_accuracy
    except grpc.RpcError as e:
        print(f"Error connecting to client {client_id}: {e}")
        return 0.0


def train_clients_thread():
    global global_weights, current_round
    i = 0
    while i < MAX_ROUNDS:
        # Se o número de clientes registrados for menor que o mínimo, aguardar 5 segundos e tentar novamente
        if len(clients) < MIN_CLIENTS:
            print("Currently connected clients:{}, need at least {}".format(len(clients), MIN_CLIENTS))
            time.sleep(2)
            continue
        else:
            clients_to_train = choose_clients()
            threads = []
            for client_id in clients_to_train:
                t = threading.Thread(target=train_client, args=(client_id,))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
        i += 1

        print("All chosen clients finished training.")

        fedav_weights = federated_average(client_weights)
        current_round += 1

        client_weights.clear()
        
        #  Avaliando todos os clientes
        threads = []
        for client_id in clients:
            t = threading.Thread(target=evaluate_clients_thread, args=(client_id, fedav_weights,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        print("All clients finished evaluation.")
        


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