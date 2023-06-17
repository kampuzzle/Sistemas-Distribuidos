import json
import paho.mqtt.client as mqtt
import hashlib
import random
import time
import sys

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
                 client,
                 number_of_clients,
                 min_clients_to_train,
                 max_rounds,
                 accuracy_threshold,
                 clients_on_network):
        self.print_("Controlador iniciado")
        self.tabela = {}
        self.endereco = broker
        self.cliente = client

        self.id = id

        self.number_of_clients = number_of_clients
        self.min_clients_to_train = min_clients_to_train
        self.max_rounds = max_rounds
        self.accuracy_threshold = accuracy_threshold
        self.clients_on_network = clients_on_network

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


    def new_round(self):
        self.print_("Iniciando nova rodada")
        # Escolhendo os clientes que irão treinar escolhendo os ids do atributo clients_on_network
        self.print_("Escolhendo os clientes que irão treinar")
        if self.id in self.clients_on_network:
            self.clients_on_network.remove(self.id)
        self.clients_to_train = random.choices(self.clients_on_network, k=self.min_clients_to_train)
        self.print_("Clientes escolhidos: {}".format(self.clients_to_train))
        self.tabela_votos = {}
         
        # Enviando mensagem para os clientes
        self.print_("Enviando mensagem para os clientes")
        self.publicar('sd/start_training', json.dumps({"round": self.round, "clients_on_network": self.clients_to_train}))

    def on_solution(self, client, userdata, message):	
        self.print_("Recebendo solução")
        time.sleep(5)
        dados = json.loads(message.payload.decode())
        client_id = dados["client_id"]
        round = dados["round"]
        weights = dados["weights"]

        self.tabela[client_id] = weights

        if len(self.tabela) == number_of_clients:
            self.print_("Todos os pesos recebidos. Calculando média federada")
            new_weights = federated_average(list(self.tabela.values()))
            global_model.set_weights(new_weights)
            self.print_("Enviando novo modelo para os treinadores")
            self.publicar('sd/new_model', json.dumps({"round": round, "weights": new_weights}))
            self.tabela = {}

            accuracy = self.evaluate()
            self.print_("Acurácia do modelo: {}".format(accuracy))
            if accuracy >= self.accuracy_threshold: 
                self.print_("Acurácia atingida. Encerrando treinamento")
                self.publicar('sd/stop_training', json.dumps({"round": round}))
                self.cliente.loop_stop()
                sys.exit(0)
            
            if round >= self.max_rounds:
                self.print_("Número máximo de rodadas atingido. Encerrando treinamento")
                self.publicar('sd/stop_training', json.dumps({"round": round}))
                self.cliente.loop_stop()
                sys.exit(0)
        
            self.print_("Iniciando nova rodada")
    
    def evaluate(self):
        x_test = np.load('teste/x_test.npy')
        y_test = np.load('teste/y_test.npy')
       
        _, accuracy = global_model.evaluate(x_test, y_test, verbose=0)
        return accuracy


        

            
    
 

    def start(self):
        self.print_("Iniciando controlador")
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        time.sleep(5)
        self.new_round()
        self.cliente.loop_start()

        while True:
            time.sleep(1)

        

     

        