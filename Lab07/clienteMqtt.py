
import random
from paho.mqtt import client as mqtt
import time 
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from controlador import Controlador
from minerador import Minerador


from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

from cryptography.hazmat.primitives import serialization
import binascii
from cryptography.hazmat.primitives.serialization import load_pem_public_key


RED = '\033[31m'
ENDC = '\033[m'

def convert_to_integer(string):
    try:
        ascii_values = [str(ord(char)) for char in string]
        integer = int(''.join(ascii_values))
        return integer
    except:
        return 0

class Cliente(): 
    # Inicializar o cliente com um id aleatório e se conectar ao broker
    def __init__(self, broker: str, n: int):
        self.id = random.randint(0,100000)
        
        # self.node id é um hexadecimal aleatorio que repersenta um numero de 32 bits (binario)
        self.node_id = random.randint(0, 2**32 - 1)
        self.node_id = hex(self.node_id)

        self.broker = broker
        self.client = mqtt.Client(str(self.id))
       
        self.controller = None


        self.min_clients = n
        self.clients_on_network = {}	
        self.tabela_votos = {}

        self.private_key, self.public_key = self.generate_public_private_key()

    # Define the function
    def generate_public_private_key(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024
        )
        public_key = private_key.public_key()
        return private_key, public_key

    def print_(self, texto):
        print(RED, "Cliente ", self.id, ENDC, " | ", texto)
    
    def publicar(self, fila, mensagem):
        r = self.client.publish(fila, mensagem)

    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.client.subscribe(fila)
        self.client.message_callback_add(fila, callback)

    def votar(self):
        vote = random.randint(0, len(self.clients_on_network.keys()) -1)
        vote = list(self.clients_on_network.keys())[vote]


        signature = self.assinar_mensagem(self.private_key, bytes(vote, 'utf-8'))

        msg = json.dumps({"node_id": self.node_id, 
                          "vote": vote, 
                          "signature": signature.hex()
                        })
        self.publicar("sd/voting", msg)
        
        if self.clients_on_network[vote] not in self.tabela_votos:
            self.tabela_votos[self.clients_on_network[vote]] = 0
        self.tabela_votos[self.clients_on_network[vote]] += 1 
        
    def assinar_mensagem(self, private_key, message):
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verificar_assinatura(self, public_key, message, signature):

        public_key = binascii.unhexlify(public_key)

        public_key = load_pem_public_key(public_key)

        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

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
                if convert_to_integer(id_votado) > convert_to_integer(vencedor): 
                    vencedor = id_votado
        self.print_("O vencedor é " + str(vencedor))
        self.tabela_votos = {}

        self.controller = vencedor


    def on_init(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
    
        self.clients_on_network[message["node_id"]] = None
        

    
    
    def on_voting(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))

        node_id = message["node_id"]
        signature = message["signature"]

        vote = message["vote"]
        
        if not self.verificar_assinatura(self.clients_on_network[node_id], vote.encode(), binascii.unhexlify(signature)):
            self.print_("Assinatura inválida")
            return
        
        self.tabela_votos[node_id] = message["vote"]
        if len(self.tabela_votos) == len(self.clients_on_network):
            self.definir_vencedor()
            self.tabela_votos = {}
            

    def on_pubkey(self, client, userdata, message):
        message = json.loads(message.payload.decode('utf-8'))
        node_id = message["node_id"]
        public_key = message["public_key"]


        self.clients_on_network[node_id] = public_key
        # Armazenar a chave pública do nó na lista de nós



    def on_connect(self, client, userdata, flags, rc):
        self.print_("Conectado ao broker")
        self.assinar("sd/init", self.on_init)
        self.assinar("sd/pubkey", self.on_pubkey)
        self.assinar("sd/voting", self.on_voting)
  

    def start(self): 
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker)
        self.client.loop_start()
        
        self.print_(texto="Iniciando o cliente")
        time.sleep(1.5)
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.client.publish("sd/init", json.dumps({"node_id": self.node_id}))
        time.sleep(1.5)
        self.client.publish("sd/pubkey", json.dumps({"node_id": self.node_id, "public_key": public_key_bytes.hex()}))

        self.votar()

        while True:
            time.sleep(0.01)
            
            if self.controller is not None:
                break
        
        if self.controller == self.node_id:
            c =  Controlador(self.broker,self.id, self.client, self.node_id, self.clients_on_network,self.private_key )
            c.start() 
        else:
            controller_public_key = self.clients_on_network[self.controller]
            m = Minerador(self.broker, self.id, self.client, self.node_id, self.clients_on_network, self.private_key, controller_public_key )
            m.start()


