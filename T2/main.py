from clienteMqtt import Cliente
import random
import threading
import sys
import pandas as pd
from matplotlib import pyplot as plt


NUM_CLIENTS = 5 # Número de clientes a serem criados
MIN_CLIENT_TO_TRAIN = 3 # Quantidade mínima de clientes participando em cada round
MAX_ROUNDS = 15 # Quantidade máxima de rounds necessários para concluir o treinamento
TARGET_ACCURACY = 0.999 # Meta de acurácia





if __name__ == "__main__":

    clientes = []

    # se um segundo argumento for passado, atribuia o ip do broker
    if len(sys.argv) > 2:
        broker = sys.argv[2]
    else:
        broker = "localhost"
    data_num = 1
    threads = []
    # Criar uma thread para cada cliente e iniciar a thread
    for i in range(int(NUM_CLIENTS)):
        cliente = Cliente(broker,
                          NUM_CLIENTS,
                          MIN_CLIENT_TO_TRAIN,
                          MAX_ROUNDS, TARGET_ACCURACY)
        print("Criando cliente ", cliente.id)
        clientes.append(cliente)
        t = threading.Thread(target=cliente.start, args=(data_num,))
        t.start()
        data_num += 1
        threads.append(t)

    # wait to join 
    for t in threads:
        t.join()

    print("Finalizando")

