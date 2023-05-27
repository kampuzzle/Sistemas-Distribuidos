from clienteMqtt import Cliente
import random
import threading
import sys


if __name__ == "__main__":
    num_clients = sys.argv[1]

    clientes = []

    
    threads = []
    # Criar uma thread para cada cliente e iniciar a thread
    for i in range(int(num_clients)):
        cliente = Cliente("broker.emqx.io", int(num_clients))
        print("Criando cliente ", cliente.id)
        clientes.append(cliente)
        t = threading.Thread(target=cliente.start)
        t.start()
        threads.append(t)


