import json
import paho.mqtt.client as mqtt
import hashlib
import random
import time
import sys
import numpy as np
import model

BLUE = '\033[34m'

ENDC = '\033[m'

PINK = '\033[35m'

global_model = model.define_model((28, 28, 1), 10)



def federated_average(weights):
    new_weights = []
    for weights_list_tuple in zip(*weights):
        new_weights.append(
            np.array([np.array(weights_).mean(axis=0) for weights_ in zip(*weights_list_tuple)]))
    return new_weights

class Controlador():

    def __init__(self, broker,
                 id,
                 number_of_clients,
                 min_clients_to_train,
                 max_rounds,
                 accuracy_threshold,
                 clients_on_network,
                 data_num):
        self.print_("Controlador iniciado")
        self.tabela = {}
        self.endereco = broker

        self.id = id

        self.number_of_clients = number_of_clients
        self.min_clients_to_train = min_clients_to_train
        self.max_rounds = max_rounds
        self.accuracy_threshold = accuracy_threshold
        self.clients_on_network = clients_on_network
        self.dataset_number = data_num

        self.acuracias = []
        self.round = 0

    def print_(self, texto):
        print(BLUE,"Controlador ", " | ",ENDC, texto)

    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.cliente.subscribe(fila)
        self.cliente.message_callback_add(fila, callback)

    def publicar(self, fila, mensagem):
        self.cliente.publish(fila, mensagem)


    def on_connect(self, client, userdata, flags, rc):
        self.print_("Conectado ao broker!")
        self.assinar('sd/solution', self.on_solution)
        self.assinar('sd/end_result',self.on_end_result)


    def new_round(self):
        self.print_("Iniciando nova rodada")
        # Escolhendo os clientes que irão treinar escolhendo os ids do atributo clients_on_network
        self.print_("Escolhendo os clientes que irão treinar")
        if self.id in self.clients_on_network:
            self.clients_on_network.remove(self.id)

        self.print_(self.clients_on_network)   
        # choose clients for training without repetition 
        self.clients_to_train = random.sample(self.clients_on_network, self.min_clients_to_train)
        self.print_("Clientes escolhidos: {}".format(self.clients_to_train))
        self.tabela_votos = {}
         
        # Enviando mensagem para os clientes
        self.print_("Enviando mensagem para os clientes")
        self.publicar('sd/start_training', json.dumps({"round": self.round, "clients_on_network": self.clients_to_train}))

    def on_solution(self, client, userdata, message):	
        self.print_("Recebendo solução")
        dados = json.loads(message.payload.decode())
        client_id = dados["client_id"]
        round = dados["round"]
        weights = dados["weights"]

        self.tabela[client_id] = weights


        if len(self.tabela) == self.min_clients_to_train:
            self.print_("Todos os pesos recebidos. Calculando média federada")
            new_weights = federated_average(list(self.tabela.values()))
            global_model.set_weights(new_weights)
            converted_weights = []
            for e in new_weights: 
                converted_weights.append(e.tolist())

            self.print_("Enviando novo modelo para os treinadores")
            self.publicar('sd/new_model', json.dumps({"round": round, "weights": converted_weights}))
            self.tabela = {}

            accuracy = self.evaluate()
            self.print_("Acurácia do modelo: {}".format(accuracy))
            if accuracy >= self.accuracy_threshold: 
                self.print_("Acurácia atingida. Encerrando treinamento")
                self.publicar('sd/stop_training', json.dumps({"round": round}))
            
            elif round >= self.max_rounds:
                self.print_("Número máximo de rodadas ating ido. Encerrando treinamento")
                self.publicar('sd/stop_training', json.dumps({"round": round}))
                
            else: 
                self.print_("Iniciando nova rodada")
                self.round += 1

                self.new_round()

    def on_end_result(self, client, userdata, message):
        self.print_("Recebendo resultado final")
        # Rebendo id e a acurácia do cliente
        dados = json.loads(message.payload.decode())
        client_id = dados["client_id"]
        accuracy = dados["accuracy"]

        self.acuracias.append(accuracy)


        if len(self.acuracias) == self.min_clients_to_train:
            s = 0
            for a in self.acuracias:
                s += a
            s = s/len(self.acuracias)
            
            self.print_("Média global de acurácia: {}".format(s))
            self.print_("Encerrando controlador")
            self.cliente.loop_stop()
            exit()

    
    def evaluate(self):
       
        x_test = np.load("teste/x_test_{}.npy".format(self.dataset_number))
        y_test = np.load("teste/y_test_{}.npy".format(self.dataset_number))       

        x_pred = global_model.predict(x_test)

        accuracy = 0
        for i in range(len(x_pred)):
            if np.argmax(x_pred[i]) == np.argmax(y_test[i]):
                accuracy += 1

        
        accuracy = accuracy/len(x_pred)
        
          



        
        return accuracy

    def start(self):
        self.print_("Iniciando controlador")
        self.cliente = mqtt.Client(str(self.id))
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        time.sleep(5)
        self.new_round()
        self.cliente.loop_start()

        while True:
            time.sleep(1)

        

     

        