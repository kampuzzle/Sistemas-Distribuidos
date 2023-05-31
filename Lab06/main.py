from clienteMqtt import Cliente
import random
import threading
import sys


if __name__ == "__main__":
    num_clients = sys.argv[1]

    clientes = []

    # se um segundo argumento for passado, atribuia o ip do broker
    if len(sys.argv) > 2:
        broker = sys.argv[2]
    else:
        broker = "broker.emqx.io"
    
    threads = []
    # Criar uma thread para cada cliente e iniciar a thread
    for i in range(int(num_clients)):
        cliente = Cliente(broker, int(num_clients))
        print("Criando cliente ", cliente.id)
        clientes.append(cliente)
        t = threading.Thread(target=cliente.start)
        t.start()
        threads.append(t)


