
import random
from paho.mqtt import client as mqtt

class Cliente: 
    # Inicializar o cliente com um id aleatório e se conectar ao broker
    def __init__(self, broker):
        self.id = random.randint(0, 1000)
        self.client = mqtt.Client(str(self.id))
        self.client.connect(broker)
        self.client.loop_start()

    def publicar(self, fila, mensagem):
        # print("Publicando na fila", fila, "a mensagem", mensagem)
        r = self.client.publish(fila, mensagem)

    def assinar(self, fila, callback):
        self.client.subscribe(fila)
        self.client.on_message = callback

    def print_(self, texto):
        print("Cliente ", self.id, " | ", texto)
    

