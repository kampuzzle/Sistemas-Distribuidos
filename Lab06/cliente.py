import json
import paho.mqtt.client as mqtt

# Configurações do broker MQTT
broker_address = "localhost"  # Endereço do broker MQTT (por exemplo, EMQX)
broker_port = 1883  # Porta do broker MQTT

# Callback para quando o cliente se conecta ao broker
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT")
    client.subscribe("sd/solution")  # Subscreve no tópico de soluções

# Callback para quando o cliente recebe uma mensagem do broker
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    data = json.loads(payload)
    client_id = data["ClientID"]
    transaction_id = data["TransactionID"]
    solution = data["Solution"]
    
    # Processar a solução recebida
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

# Mantém o cliente em execução até ser interrompido
try:
    while True:
        pass
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
    print("Cliente MQTT desconectado")
