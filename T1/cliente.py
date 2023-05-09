# Importar as bibliotecas necessárias
import grpc
import numpy as np
import federado_pb2
import federado_pb2_grpc

import model 

# Definir o ID, o IP e a porta do cliente
CLIENT_ID = "client1"
CLIENT_IP = "localhost"
CLIENT_PORT = 50051

# Definir o IP e a porta do servidor
SERVER_IP = "localhost"
SERVER_PORT = 8080



class ClientLearningServicer(federado_pb2_grpc.FederatedLearningServicer):

  def StartTraining(self, request, context):
    # Obter o número do round atual da requisição
    current_round = request.current_round

    # Obter os pesos do modelo global da requisição como uma lista de arrays numpy
    global_weights = [np.array(w.weight) for w in request.global_weights]

    # Atribuir os pesos do modelo global ao modelo local do cliente
    global_model.set_weights(global_weights)

    # Carregar os dados locais do cliente usando o número do round como índice
    x_train = np.load(f"treino/x_train_{current_round}.npy")
    y_train = np.load(f"treino/y_train_{current_round}.npy")

    # Treinar o modelo local do cliente usando os dados locais por uma época
    global_model.fit(x_train, y_train, epochs=1)

    # Obter os pesos do modelo local do cliente após o treinamento
    local_weights = global_model.get_weights()

    # Obter o número de amostras da base de dados local
    local_samples = len(x_train)

    # Imprimir uma mensagem informando que o treinamento foi concluído
    print(f"Training completed for round {current_round}")

    # Retornar uma resposta com os pesos do modelo local e o número de amostras como uma lista de Weight messages
    return federado_pb2.StartTrainingResponse(local_weights=[w for w in local_weights], local_samples=local_samples)


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
    print(f"Client {CLIENT_ID} achieved accuracy {accuracy} on round {register_response.current_round}")

    # Retornar uma resposta com a acurácia
    return federado_pb2.EvaluateModelResponse(accuracy=accuracy)





# Criar um canal gRPC para se comunicar com o servidor
channel = grpc.insecure_channel(f"{SERVER_IP}:{SERVER_PORT}")

# Criar um stub para acessar o serviço de aprendizado federado do servidor
stub = federado_pb2_grpc.FederatedLearningStub(channel)

# Registrar o cliente no servidor enviando uma requisição com o ID, o IP e a porta do cliente
register_request = federado_pb2.RegisterClientRequest(client_id=CLIENT_ID, client_ip=CLIENT_IP, client_port=CLIENT_PORT)

# Receber a resposta do servidor com o código de confirmação e o número do round atual
register_response = stub.RegisterClient(register_request)

# Imprimir uma mensagem informando que o cliente foi registrado com sucesso
print(f"Client {CLIENT_ID} registered with confirmation code {register_response.confirmation_code} and current round {register_response.current_round}")


# modelo 
global_model = model.define_model((28, 28, 1), 10)


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
  start_training_response = federado_pb2.StartTrainingResponse(local_weights=[w for w in local_weights], local_samples=local_samples)

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
  evaluate_model_response = stub.EvaluateModelResponse(global_weights=[w for w in global_weights], accuracy=accuracy)

  # Receber a próxima requisição de avaliação do servidor com os pesos do modelo global atualizados
  evaluate_model_request = stub.EvaluateModel(evaluate_model_response)

  # Atualizar a resposta de registro com os pesos do modelo global
  register_response.global_weights = evaluate_model_request.global_weights

