
import random
from paho.mqtt import client as mqtt
import time 
import json

from controlador import Controlador
from minerador import Minerador


RED = '\033[31m'
ENDC = '\033[m'



class Cliente(): 
    # Inicializar o cliente com um id aleatório e se conectar ao broker
    def __init__(self, broker: str, n: int):
        self.id = random.randint(0, 1000)
        self.broker = broker
        self.client = mqtt.Client(str(self.id))
       
        self.controller = None

        self.min_clients = n
        self.clients_on_network = []
        self.tabela_votos = {}

    def print_(self, texto):
        print(RED, "Cliente ", self.id, ENDC, " | ", texto)
    
    def publicar(self, fila, mensagem):
        r = self.client.publish(fila, mensagem)

    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.client.subscribe(fila)
        self.client.message_callback_add(fila, callback)

    def votar(self):
        vote = random.randint(0, len(self.clients_on_network) -1)
        msg = json.dumps({"client_id": self.id, 
                          "vote": self.clients_on_network[vote]
                        })
        self.publicar("sd/voting", msg)
        
        if self.clients_on_network[vote] not in self.tabela_votos:
            self.tabela_votos[self.clients_on_network[vote]] = 0
        self.tabela_votos[self.clients_on_network[vote]] += 1 
        

    def definir_vencedor(self):
        maximo = 0
        vencedor = None
        for client_id in self.tabela_votos:
            if self.tabela_votos[client_id] > maximo:
                maximo = self.tabela_votos[client_id]
                vencedor = client_id
        self.print_("O vencedor é " + str(vencedor))
        self.clients_on_network = []
        self.tabela_votos = {}

        self.controller = vencedor


    def on_init(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
        self.clients_on_network.append(message["client_id"])

        # Se o número de clientes na rede for maior que min_clients,
        # publicar uma mensagem de votação na fila sd/voting
        if len(self.clients_on_network) >= self.min_clients:
            self.votar()

  

    
    def on_voting(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
        self.tabela_votos[message["client_id"]] = message["vote"]
        if len(self.tabela_votos) == len(self.clients_on_network):
            self.definir_vencedor()
            self.tabela_votos = {}


    def on_connect(self, client, userdata, flags, rc):
        self.print_("Conectado ao broker")
        self.assinar("sd/init", self.on_init)
        self.assinar("sd/voting", self.on_voting)
  

    def start(self): 
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker)
        self.client.loop_start()
        
        self.print_(texto="Iniciando o cliente")
        time.sleep(2)
        self.client.publish("sd/init", json.dumps({"client_id": self.id}))

        while True:
            time.sleep(0.01)
            if self.controller is not None:
                break
        
        if self.controller == self.id:
            c =  Controlador(self.broker,self.id, self.client)
            c.start() 
        else:
            m = Minerador(self.broker, self.id, self.client)
            m.start()


