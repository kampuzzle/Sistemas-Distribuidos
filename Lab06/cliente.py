import json
import paho.mqtt.client as mqtt
import hashlib

class Cliente:
    def __init__(self, broker_address, broker_port):
        self.broker_address = broker_address
        self.broker_port = broker_port
        
        # Cria um cliente MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    # Callback para quando o cliente se conecta ao broker
    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT")
        self.client.subscribe("sd/challenge")

    # Callback para quando o cliente recebe uma mensagem
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        
        if topic == "sd/challenge":
            self.processar_desafio(payload)

    # Envia uma solução para o controlador
    def enviar_solucao(self, client_id, transaction_id, solution):
        data = {
            "ClientID": client_id,
            "TransactionID": transaction_id,
            "Solution": solution
        }
        payload = json.dumps(data)
        self.client.publish("sd/solution", payload)

    # Processa um desafio recebido do controlador
    def processar_desafio(self, payload):
        data = json.loads(payload)
        transaction_id = data["TransactionID"]
        challenge = data["Challenge"]
        
        # Resolva o desafio
        solution = self.resolver_desafio(challenge)
        
        # Envie a solução para o controlador
        client_id = 123  # Substitua pelo ID do cliente real
        self.enviar_solucao(client_id, transaction_id, solution)

    # Resolve um desafio criptográfico
    def resolver_desafio(self, challenge):
        # Implemente a lógica para resolver o desafio aqui
        # Neste exemplo, usamos o SHA-1 para calcular a solução
        challenge_str = str(challenge)
        solution = hashlib.sha1(challenge_str.encode()).hexdigest()
        return solution

    # Inicia o cliente
    def start(self):
        # Conecta ao broker MQTT
        self.client.connect(self.broker_address, self.broker_port, 60)
        
        # Inicia o loop de rede do cliente MQTT
        self.client.loop_start()

        


# Configurações do broker MQTT
broker_address = "broker.emqx.io"  # Endereço do broker MQTT (por exemplo, EMQX)
broker_port = 1883  # Porta do broker MQTT

# Cria uma instância do cliente
cliente = Cliente(broker_address, broker_port)

# Inicia o cliente
cliente.start()
