from minerador import Minerador
from controlador import Controlador
from clienteMqtt import Cliente
import random

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


# Transformar os outros clientes em mineradores
for cliente in clientes:
    if cliente != controlador:
        cliente.__class__ = Minerador
        cliente.__init__()

# Iniciar a comunicação entre o controlador e os mineradores
controlador.novo_desafio()
