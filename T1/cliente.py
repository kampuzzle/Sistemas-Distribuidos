# Importar as bibliotecas necessárias
import grpc
import numpy as np
import federado_pb2
import federado_pb2_grpc
from concurrent import futures

import sys
import model 

# Definir o ID, o IP e a porta do cliente
CLIENT_ID = None
CLIENT_IP = "localhost"
CLIENT_PORT = list(range(50051, 50061))  #  Range de portas para os clientes
# Definir o IP e a porta do servidor
SERVER_IP = "localhost"
SERVER_PORT = 8080

# modelo 
global_model = model.define_model((28, 28, 1), 10)

local_weights = global_model.get_weights()

# Dado um id, retorna um número entre 1 e 3
def getDatasetNumber(id): 
    return id % 3 + 1



def reshapeWeight(server_weight, client_weight):
    reshape_weight = []

    for layer_weights in client_weight:
        n_weights = np.prod(layer_weights.shape)
        reshape_weight.append(np.array(server_weight[:n_weights]).reshape(layer_weights.shape))
        server_weight = server_weight[n_weights:]

    return reshape_weight


class ClientLearningServicer(federado_pb2_grpc.ClientLearningServicer):

  def StartTraining(self, request, context):
    global local_weights
    # Obter o número do round atual da requisição
    current_round = request.current_round

    
    # Carregar os dados locais do cliente usando o número do round atual como índice
    x_train = np.load(f"treino/x_train_{CLIENT_ID}.npy")
    y_train = np.load(f"treino/y_train_{CLIENT_ID}.npy")

    print(f"Training started for round {current_round}")

    # Treinar o modelo local do cliente usando os dados locais por uma época
    global_model.fit(x_train, y_train, epochs=1)


    # Transformar pesos em um array de floats, tranformar o shape do vetor para uma unica dimensão
    local_weights_flatten = [w.flatten() for w in global_model.get_weights()]
    local_weights_flatten = np.concatenate(local_weights_flatten).tolist()


    # Retornar uma resposta com os pesos do modelo local e o número de amostras como uma lista de Weight messages
    return federado_pb2.StartTrainingResponse(local_weights=local_weights_flatten, local_samples=len(x_train))


  def EvaluateModel(self, request, context):
    global local_weights
    
    # Carregar os dados locais do cliente usando o número do round como índice
    x_test = np.load("teste/x_test.npy")
    y_test = np.load("teste/y_test.npy")

    # Avaliar o modelo local do cliente usando os dados de teste locais e os pesos do modelo global atualizados
    loss, accuracy = global_model.evaluate(x_test, y_test)

     # Obter os pesos do modelo global da requisição como uma lista de arrays numpy
    global_weights = request.global_weights

    print(f"Received global weights with {len(global_weights)} elements")
    local_weights = reshapeWeight(global_weights, local_weights)
    global_model.set_weights(local_weights)
  
    # Imprimir uma mensagem informando a acurácia obtida pelo cliente
    print(f"Obtained accuracy is {accuracy}")

    # Retornar uma resposta com a acurácia
    return federado_pb2.EvaluateModelResponse(accuracy=accuracy)


def serve(port):
  # Criar um servidor gRPC para receber requisições de treinamento e avaliação do servidor
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
  federado_pb2_grpc.add_ClientLearningServicer_to_server(ClientLearningServicer(), server)
  server.add_insecure_port(f"{CLIENT_IP}:{port}")
  server.start()
  server.wait_for_termination()
  


if __name__ == "__main__":

  if len(sys.argv) > 1:
    CLIENT_ID = sys.argv[1]
    port = CLIENT_PORT[int(CLIENT_ID) - 1]
  else:
    print("Client ID not provided")
    exit(1) 


  # Criar um canal gRPC para se comunicar com o servidor
  channel = grpc.insecure_channel(f"{SERVER_IP}:{SERVER_PORT}")

  # Criar um stub para acessar o serviço de aprendizado federado do servidor
  stub = federado_pb2_grpc.FederatedLearningStub(channel)

  # Registrar o cliente no servidor enviando uma requisição com o ID, o IP e a porta do cliente
  register_request = federado_pb2.RegisterClientRequest(client_id=CLIENT_ID, client_ip=CLIENT_IP, client_port=port)

  # Receber a resposta do servidor com o código de confirmação e o número do round atual
  register_response = stub.RegisterClient(register_request)

  # Imprimir uma mensagem informando que o cliente foi registrado com sucesso
  print(f"Client {CLIENT_ID} registered with confirmation code {register_response.confirmation_code} and current round {register_response.current_round}")

  # Iniciar o servidor gRPC
  serve(port)


