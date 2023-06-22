
import random
from paho.mqtt import client as mqtt
import time 
import json

from controlador import Controlador
from treinador import Treinador


RED = '\033[31m'
ENDC = '\033[m'



class Cliente(): 
    # Inicializar o cliente com um id aleatório e se conectar ao broker
    def __init__(self, broker: str, number_of_clients: int, min_clients_to_train: int, max_rounds: int, accuracy_threshold: float):
        self.id = random.randint(0, 65536)
        self.broker = broker
        self.client = mqtt.Client(str(self.id))

       
        self.controller = None

   
        self.clients_on_network = []
        self.tabela_votos = {}

        self.number_of_clients = number_of_clients
        self.min_clients_to_train = min_clients_to_train
        self.max_rounds = max_rounds
        self.accuracy_threshold = accuracy_threshold

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
        
        # if self.clients_on_network[vote] not in self.tabela_votos:
        #     self.tabela_votos[self.clients_on_network[vote]] = 0
        # self.tabela_votos[self.clients_on_network[vote]] += 1 
        

    def definir_vencedor(self):
        contagem_votos = {}
    
        for id_cliente, id_votado in self.tabela_votos.items():
            if id_votado in contagem_votos: 
                contagem_votos[id_votado] += 1
            else: 
                contagem_votos[id_votado] = 1

        vencedor = None
        id_maximo = -1
        maximo = -1
        for id_votado, count, in contagem_votos.items(): 
            
            if count > maximo:
                maximo = count
                vencedor = id_votado
            elif count == maximo:
                if id_votado > vencedor: 
                    vencedor = id_votado
        self.print_("O vencedor é " + str(vencedor))
        self.tabela_votos = {}

        self.controller = vencedor


    def on_init(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
        self.clients_on_network.append(message["client_id"])

        # Se o número de clientes na rede for maior que min_clients,
        # publicar uma mensagem de votação na fila sd/voting
        if len(self.clients_on_network) >= self.min_clients_to_train:
            self.votar()

    
    def on_voting(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
        self.tabela_votos[message["client_id"]] = message["vote"]
        if len(self.tabela_votos) == len(self.clients_on_network):
            self.definir_vencedor()
            self.tabela_votos = {}


    def on_stop_training(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
        self.print_("Recebido stop_training do controlador")
        self.print_("Parando o treinamento")
        self.client.disconnect()
        self.client.loop_stop()
        self.client = None
        self.controller = None
        self.start()

    def on_connect(self, client, userdata, flags, rc):
        self.print_("Conectado ao broker")
        self.assinar("sd/init", self.on_init)
        self.assinar("sd/voting", self.on_voting)
  

    def start(self, data_num): 
        self.client.on_connect = self.on_connect
        self.client.on_stop_training = self.on_stop_training
        self.client.connect(self.broker)
        self.client.loop_start()
        
        self.print_(texto="Iniciando o cliente")
        time.sleep(5)
        self.client.publish("sd/init", json.dumps({"client_id": self.id}))
        
        while True:
            time.sleep(0.01)
            
            if self.controller is not None:
                break
        
        if self.controller == self.id:
            self.client.loop_stop()

            c =  Controlador(self.broker,self.id,
                             self.number_of_clients,
                             self.min_clients_to_train,
                             self.max_rounds,
                             self.accuracy_threshold,
                             self.clients_on_network,
                             data_num)
            time.sleep(2)
            c.start() 
        else:
            self.client.loop_stop()

            m = Treinador(self.broker, self.id,data_num)
            m.start()

        self.clients_on_network = []

