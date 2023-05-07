# Importar as bibliotecas necessárias
import grpc
import numpy as np
from federated_pb2 import *
from federated_pb2_grpc import *

# Definir o ID, o IP e a porta do cliente
CLIENT_ID = "client1"
CLIENT_IP = "localhost"
CLIENT_PORT = 50051

# Definir o IP e a porta do servidor
SERVER_IP = "localhost"
SERVER_PORT = 50052

# Criar um canal gRPC para se comunicar com o servidor
channel = grpc.insecure_channel(f"{SERVER_IP}:{SERVER_PORT}")

# Criar um stub para acessar o serviço de aprendizado federado do servidor
stub = FederatedLearningStub(channel)

# Registrar o cliente no servidor enviando uma requisição com o ID, o IP e a porta do cliente
register_request = RegisterClientRequest(client_id=CLIENT_ID, client_ip=CLIENT_IP, client_port=CLIENT_PORT)

# Receber a resposta do servidor com o código de confirmação e o número do round atual
register_response = stub.RegisterClient(register_request)

# Imprimir uma mensagem informando que o cliente foi registrado com sucesso
print(f"Client {CLIENT_ID} registered with confirmation code {register_response.confirmation_code} and current round {register_response.current_round}")

# Entrar em um loop infinito para participar dos rounds de treinamento
while True:
  # Obter os pesos do modelo global do servidor como uma lista de arrays numpy
  global_weights = [np.array(w.weight) for w in register_response.global_weights]

  # Atribuir os pesos do modelo global ao modelo local do cliente
  global_model.set_weights(global_weights)

  # Carregar os dados locais do cliente usando o número do round atual como índice
  x_train = np.load(f"treino/x_train_{register_response.current_round}.npy")
  y_train = np.load(f"treino/y_train_{register_response.current_round}.npy")

  # Treinar o modelo local do cliente usando os dados locais por uma época
  global_model.fit(x_train, y_train, epochs=1)

  # Obter os pesos do modelo local do cliente após o treinamento
  local_weights = global_model.get_weights()

  # Obter o número de amostras da base de dados local
  local_samples = len(x_train)

  # Enviar os pesos do modelo local e o número de amostras ao servidor como uma resposta de treinamento
  start_training_response = StartTrainingResponse(local_weights=[Weight(weight=w) for w in local_weights], local_samples=local_samples)

  # Receber a próxima requisição de treinamento do servidor com o número do round atual e os pesos do modelo global atualizados
  start_training_request = stub.StartTraining(start_training_response)

  # Atualizar a resposta de registro com o número do round atual e os pesos do modelo global
  register_response.current_round = start_training_request.current_round
  register_response.global_weights = start_training_request.global_weights

  # Avaliar o modelo local do cliente usando os dados de teste locais e os pesos do modelo global atualizados
  x_test = np.load("teste/x_test.npy")
  y_test = np.load("teste/y_test.npy")
  global_model.set_weights(global_weights)
  loss, accuracy = global_model.evaluate(x_test, y_test)

  # Imprimir uma mensagem informando a acurácia obtida pelo cliente
  print(f"Client {CLIENT_ID} achieved accuracy {accuracy} on round {register_response.current_round}")

  # Enviar os pesos do modelo global e a acurácia ao servidor como uma resposta de avaliação
  evaluate_model_response = EvaluateModelResponse(global_weights=[Weight(weight=w) for w in global_weights], accuracy=accuracy)

  # Receber a próxima requisição de avaliação do servidor com os pesos do modelo global atualizados
  evaluate_model_request = stub.EvaluateModel(evaluate_model_response)

  # Atualizar a resposta de registro com os pesos do modelo global
  register_response.global_weights = evaluate_model_request.global_weights

