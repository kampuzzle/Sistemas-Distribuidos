import json
import paho.mqtt.client as mqtt

# Configurações do broker MQTT
broker_address = "localhost"  # Endereço do broker MQTT (por exemplo, EMQX)
broker_port = 1883  # Porta do broker MQTT

# Tabela para armazenar os registros
table = {}

# Callback para quando o cliente se conecta ao broker
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT")

# Callback para quando o cliente recebe uma mensagem do broker
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    data = json.loads(payload)
    client_id = data["ClientID"]
    transaction_id = data["TransactionID"]
    solution = data["Solution"]
    
    # Verificar se a transação já foi resolvida por outro minerador
    if transaction_id in table:
        return
    
    # Verificar a solução da transação
    # ...

    # Atualizar a tabela com o resultado da solução
    # ...

# Cria um cliente MQTT
client = mqtt.Client()

# Define as callbacks
client.on_connect = on_connect
client.on_message = on_message

# Conecta ao broker MQTT
client.connect(broker_address, broker_port, 60)

# Inicia o loop de rede do cliente MQTT
client.loop_start()

# Publica uma nova transação para os mineradores
def publish_transaction(transaction_id, challenge, solution):
    data = {
        "ClientID": -1,
        "TransactionID": transaction_id,
        "Solution": solution
    }
    client.publish("sd/solution", json.dumps(data))

# Loop principal do servidor
try:
    while True:
        # Simula a criação de uma nova transação
        transaction_id = 1  # ID da transação
        challenge = 1  # Desafio criptográfico
        solution = ""  # Solução inicial (vazio)
        
        # Publica a nova transação para os mineradores
        publish_transaction(transaction_id, challenge, solution)
        
        # Aguarda um tempo para simular a criação de uma nova transação
        # ...
        
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
    print("Servidor MQTT desconectado")
