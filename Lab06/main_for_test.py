from clienteMqtt import Cliente
import random
import threading
import sys


if __name__ == "__main__":
    num_clients = sys.argv[1]

    clientes = []
    # Criar quatro clientes e adicioná-los à lista
    for i in range(int(num_clients)):
        cliente = Cliente("broker.emqx.io",int(num_clients))
        clientes.append(cliente)


    threads = []
    for cliente in clientes:
        t = threading.Thread(target=cliente.start)
        threads.append(t)
        t.start()

