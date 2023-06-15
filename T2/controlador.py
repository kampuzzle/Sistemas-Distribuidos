import json
import paho.mqtt.client as mqtt
import hashlib
import random
import time
import sys

BLUE = '\033[34m'

ENDC = '\033[m'

PINK = '\033[35m'


class Controlador():

    # Inicializar o controlador com uma tabela vazia de transações
    def __init__(self, broker, id, client):
        self.print_("Controlador iniciado")
        self.tabela = []

        self.endereco = broker
        self.cliente = client

        self.id = id
 

    def print_(self, texto):
        print(BLUE,"Controlador ",ENDC, " | ", texto)

    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.cliente.subscribe(fila)
        self.cliente.message_callback_add(fila, callback)

    def publicar(self, fila, mensagem):
        self.cliente.publish(fila, mensagem)


    def on_connect(self, client, userdata, flags, rc):
        self.print_("Conectado ao broker!")
        self.assinar('sd/solution', self.on_solution)




    def start(self):
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        self.cliente.loop_start()

        self.loop()
