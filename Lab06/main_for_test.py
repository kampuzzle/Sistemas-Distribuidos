from minerador import Minerador
from controlador import Controlador
from clienteMqtt import Cliente
import random
import threading


clientes = []
# Criar quatro clientes e adicioná-los à lista
for i in range(4):
    cliente = Cliente("broker.emqx.io")
    clientes.append(cliente)

# Escolher um cliente aleatório para ser o controlador
controlador = random.choice(clientes)

# Transformar o cliente escolhido em um controlador
controlador.__class__ = Controlador
controlador.__init__()

threads = []

threads.append(threading.Thread(target=controlador.loop))



# Transformar os outros clientes em mineradores
for cliente in clientes:
    if cliente != controlador:
        cliente.__class__ = Minerador
        threads.append(threading.Thread(target=cliente.loop))
        cliente.__init__()


# Iniciar as threads
for thread in threads:
    thread.start()
    

for thread in threads:
    thread.join()
    


