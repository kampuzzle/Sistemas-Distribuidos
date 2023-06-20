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
    def __init__(self, broker, id_client, data_num):

        self.endereco = broker
        
        # get a number form 1 to 5, which will be the dataset that this trainer will use based on the client id
        self.dataset_number = data_num
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



    def evaluate(self):
        dataset_test_number  = int(self.dataset_number) % 5 + 1

        x_test = np.load("teste/x_test_{}.npy".format(dataset_test_number))
        y_test = np.load("teste/y_test_{}.npy".format(dataset_test_number))       
        
        _, accuracy = global_model.evaluate(x_test, y_test, verbose=0)
        
        return accuracy
    
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
        self.print_("Treinando com o dataset {}".format(self.dataset_number))
        self.model.fit(X, y, epochs=1)
        self.local_weights = self.model.get_weights()
       


        converted_weights = []
        for e in self.local_weights: 
            converted_weights.append(e.tolist())

        mensagem = json.dumps({"client_id": self.id, "round": round,  "weights":converted_weights })
        self.print_("Treino terminado, enviando peso...")
        self.publicar('sd/solution', mensagem)

    def on_new_model(self, client, userdata, message):
        self.print_("Recebendo novo modelo")
        dados = json.loads(message.payload.decode())
        
        converted_weights = []
        for e in dados["weights"]: 
            converted_weights.append(np.array(e))
       
        self.model.set_weights(converted_weights)
        self.print_("pesos setados")
   
    def on_connect(self, client, userdata, flags, rc):
        self.assinar('sd/start_training', self.on_start_training)
        self.assinar('sd/new_model', self.on_new_model)
        self.assinar('sd/stop_training', self.on_stop_training)

    def on_stop_training(self, client, userdata, message):
        self.print_("Parando treinamento")


        accuracy = self.evaluate()

        self.publicar('sd/end_result', json.dumps({"client_id": self.id, "accuracy": accuracy}))


        self.cliente.loop_stop()
        sys.exit(0)



        
            
    
    def start(self):
        self.cliente = mqtt.Client(str(self.id))
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        self.cliente.loop_start()


