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
NUM_CLIENTS = 3 # Número de clientes a serem escolhidos em cada round
MIN_CLIENTS = 2 # Quantidade mínima de clientes participando em cada round
MAX_ROUNDS = 10 # Quantidade máxima de rounds necessários para concluir o treinamento
TARGET_ACCURACY = 0.9 # Meta de acurácia
TIMEOUT = 10 # Timeout de conexão com os clientes em segundos

# Definir o modelo global usando Keras
global_model = define_model((28, 28, 1), 10)

# Compilar o modelo global com otimizador SGD e função de perda entropia cruzada categórica
global_model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

# Obter os pesos iniciais do modelo global
global_weights = global_model.get_weights()

client_weights = {}

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

  # # Iniciar o treinamento de um cliente
  # def StartTraining(self, request, context):
  #   # Obter o número do round atual da requisição
  #   current_round = request.current_round

  #   # Obter os pesos do modelo global da requisição como uma lista de arrays numpy
  #   global_weights = [np.array(w.weight) for w in request.global_weights]


  #   if len(clients) < MIN_CLIENTS:
  #     # Retornar uma resposta com os pesos do modelo global e o número de amostras como uma lista de Weight messages
  #     return federado_pb2.StartTrainingResponse(local_weights=[w for w in global_weights], local_samples=[0])



  #   # Retornar uma resposta com os pesos do modelo local e o número de amostras como uma lista de Weight messages
  #   return federado_pb2.StartTrainingResponse(local_weights=[w for w in local_weights], local_samples=local_samples)

  def EvaluateModel(self, request, context):
    # Obter o número do round atual da requisição
    current_round = request.current_round

    # Obter os pesos do modelo global da requisição como uma lista de arrays numpy
    global_weights = [np.array(w.weight) for w in request.global_weights]

    # Atribuir os pesos do modelo global ao modelo local do cliente
    global_model.set_weights(global_weights)

    # Carregar os dados locais do cliente usando o número do round como índice
    x_test = np.load("teste/x_test.npy")
    y_test = np.load("teste/y_test.npy")

    # Avaliar o modelo local do cliente usando os dados de teste locais e os pesos do modelo global atualizados
    loss, accuracy = global_model.evaluate(x_test, y_test)

    # Imprimir uma mensagem informando a acurácia obtida pelo cliente
    # print(f"Client {CLIENT_ID} achieved accuracy {accuracy} on round {register_response.current_round}")

    # Retornar uma resposta com a acurácia
    return federado_pb2.EvaluateModelResponse(accuracy=accuracy)     

def choose_clients():
 
  # Criar uma lista com os IDs dos clientes registrados
  client_ids = list(clients.keys())

  # Embaralhar a lista de IDs
  random.shuffle(client_ids)

  # Obter os primeiros IDs da lista embaralhada
  chosen_clients = client_ids[:NUM_CLIENTS]

  # Imprimir uma mensagem informando os clientes escolhidos
  print(f"Chosen clients: {chosen_clients}")

  # Retornar os IDs dos clientes escolhidos
  return chosen_clients


def federatedAveraging():
    # Fazer a média dos pesos dos clientes
    averaged_weights = []

    # Para cada camada do modelo global
    for layer in range(len(global_weights)):
        # Criar uma lista para armazenar os pesos da camada
        layer_weights = []

        # Para cada cliente
        for client_id in client_weights:
            # Adicionar os pesos da camada do cliente à lista
            layer_weights.append(client_weights[client_id][layer])

        # Fazer a média dos pesos da camada
        averaged_layer_weights = np.mean(layer_weights, axis=0)

        # Adicionar os pesos da camada à lista
        averaged_weights.append(averaged_layer_weights)
    
    return averaged_weights


def train_client(client_id):
    client_ip, client_port, confirmation_code = clients[client_id]
    print(f"Training client {client_id}...")
    channel = grpc.insecure_channel(f"{client_ip}:{client_port}")
    stub = federado_pb2_grpc.ClientLearningStub(channel)
    try:
        response = stub.StartTraining(federado_pb2.StartTrainingRequest(confirmation_code=confirmation_code, current_round=0), timeout=TIMEOUT)
        client_weights[client_id] = [np.array(w.weight) for w in response.local_weights] 
    except grpc.RpcError as e:
        print(f"Error connecting to client {client_id}: {e}")
    print(f"Client {client_id} finished training.")



def train_clients_thread():
    while True:
        # Se o número de clientes registrados for menor que o mínimo, aguardar 5 segundos e tentar novamente
        if len(clients) < MIN_CLIENTS:
            print("Waiting for more clients...")
            time.sleep(5)
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
        global_weights = federatedAveraging()

        # Evaluate all clients 
        for client_id in clients:
            client_ip, client_port, confirmation_code = clients[client_id]
            print(f"Evaluating client {client_id}...")
            channel = grpc.insecure_channel(f"{client_ip}:{client_port}")
            stub = federado_pb2_grpc.ClientLearningStub(channel)
            try:
                response = stub.EvaluateModel(federado_pb2.EvaluateModelRequest(confirmation_code=confirmation_code, current_round=0, global_weights=[ w for w in global_weights]), timeout=TIMEOUT)
                print(f"Client {client_id} achieved accuracy {response.accuracy}")
            except grpc.RpcError as e:
                print(f"Error connecting to client {client_id}: {e}")
            print(f"Client {client_id} finished evaluation.")


def serve():
    print("Starting server...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

    # client chooser thread
    client_chooser = threading.Thread(target=train_clients_thread)
    client_chooser.start()


    federado_pb2_grpc.add_FederatedLearningServicer_to_server(FederatedLearningServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Listening on port 8080.")
    server.wait_for_termination()

    


if __name__ == "__main__":
    serve()