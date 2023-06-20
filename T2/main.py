from clienteMqtt import Cliente
import random
import threading
import sys

NUM_CLIENTS = 2 # Número de clientes a serem criados
MIN_CLIENT_TO_TRAIN = 1 # Quantidade mínima de clientes participando em cada round
MAX_ROUNDS = 20 # Quantidade máxima de rounds necessários para concluir o treinamento
TARGET_ACCURACY = 0.999 # Meta de acurácia





if __name__ == "__main__":

    clientes = []

    # se um segundo argumento for passado, atribuia o ip do broker
    if len(sys.argv) > 2:
        broker = sys.argv[2]
    else:
        broker = "localhost"
    
    threads = []
    # Criar uma thread para cada cliente e iniciar a thread
    for i in range(int(NUM_CLIENTS)):
        cliente = Cliente(broker,
                          NUM_CLIENTS,
                          MIN_CLIENT_TO_TRAIN,
                          MAX_ROUNDS, TARGET_ACCURACY)
        print("Criando cliente ", cliente.id)
        clientes.append(cliente)
        t = threading.Thread(target=cliente.start)
        t.start()
        threads.append(t)


