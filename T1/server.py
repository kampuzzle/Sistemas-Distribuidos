import tensorflow as tf
import numpy as np
import grpc
import random
from federated_pb2 import *
from federated_pb2_grpc import *

# Definir os parâmetros do servidor
NUM_CLIENTS = 3 # Número de clientes a serem escolhidos em cada round
MIN_CLIENTS = 2 # Quantidade mínima de clientes participando em cada round
MAX_ROUNDS = 10 # Quantidade máxima de rounds necessários para concluir o treinamento
TARGET_ACCURACY = 0.9 # Meta de acurácia
TIMEOUT = 10 # Timeout de conexão com os clientes em segundos

# Definir o modelo global usando Keras
global_model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(28, 28)),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(10, activation='softmax')
])

# Compilar o modelo global com otimizador SGD e função de perda entropia cruzada categórica
global_model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

# Obter os pesos iniciais do modelo global
global_weights = global_model.get_weights()

# Criar um dicionário para armazenar os clientes registrados
clients = {}

# Criar uma classe para implementar o serviço de aprendizado federado definido no protobuf
class FederatedLearningServicer(FederatedLearningServicer):

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
    return RegisterClientResponse(confirmation_code=confirmation_code, current_round=0)

  # Iniciar o treinamento de um cliente
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
    return StartTrainingResponse(local_weights=[Weight(weight=w) for w in local_weights], local