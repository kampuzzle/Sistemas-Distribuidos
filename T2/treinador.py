import json
import paho.mqtt.client as mqtt
import hashlib
import random
import string
import sys
import numpy as np
import model
import pandas as pd

YELLOW = '\033[33m'
ENDC = '\033[m'

NUM_OF_DATASETS = 5

global_model = model.define_model((28, 28, 1), 10)

class Treinador():
    def __init__(self, broker, id_client, client):

        self.cliente = client
        self.endereco = broker
        
        # get a number form 1 to 5, which will be the dataset that this trainer will use based on the client id
        self.dataset_number = int(id_client) % int(NUM_OF_DATASETS) + 1
        self.model = global_model
        self.local_weights = None
        self.id = id_client
    
    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.cliente.subscribe(fila)
        self.cliente.message_callback_add(fila, callback)

    def publicar(self, fila, mensagem):
        r = self.cliente.publish(fila, mensagem)
        # print status 
        if r[0] == mqtt.MQTT_ERR_SUCCESS:
            self.print_("Mensagem publicada com sucesso na fila " + fila)
        elif r[0] == mqtt.MQTT_ERR_NO_CONN:
            self.print_("Erro. Cliente desconectado.")
        elif r[0] == mqtt.MQTT_ERR_QUEUE_SIZE:
            self.print_("Erro. Fila cheia.")
        else:
            self.print_("Erro. Código de erro: " + str(r[0]))



    def print_(self, texto):
        print(YELLOW,"Treinador ",  " | ",self.id,ENDC, texto)



    # Definir uma função de callback para receber os desafios do controlador na fila sd/challenge
    def on_start_training(self, client, userdata, message):
        self.print_("Hora de treinar!")
        dados = json.loads(message.payload.decode())
        round = dados["round"]
        clients_ids = dados["clients_on_network"]

        # if this trainer is not in the list of clients that will train, then it will not train
        if self.id not in clients_ids:
            self.print_("Não estou na lista de clientes que irão treinar")
            return

        X = np.load("treino/x_train_{}.npy".format(self.dataset_number))
        y = np.load("treino/y_train_{}.npy".format(self.dataset_number))
        print("Treinando com o dataset {}".format(self.dataset_number))
        self.model.fit(X, y, epochs=1)
        self.local_weights = self.model.get_weights()

        # convert to a json acceptable format
        local_weights = pd.DataFrame( self.local_weights).to_json(orient='values')

        mensagem = json.dumps({"client_id": self.id, "round": round })
                            # "weights":local_weights})
        self.print_("Treino terminado, enviando peso...")
        self.publicar('sd/solution', mensagem)

    def on_new_model(self, client, userdata, message):
        self.print_("Recebendo novo modelo")
        dados = json.loads(message.payload.decode())
        weights = dados["weights"]
        self.model.set_weights(weights)
   
    def on_connect(self, client, userdata, flags, rc):
        self.assinar('sd/start_training', self.on_start_training)
        self.assinar('sd/new_model', self.on_new_model)

    def on_stop_training(self, client, userdata, message):
        self.print_("Parando treinamento")
        self.model.set_weights(self.local_weights)
        self.cliente.loop_stop()
        sys.exit(0)



        
            
    
    def start(self):
        
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        self.cliente.loop_start()

