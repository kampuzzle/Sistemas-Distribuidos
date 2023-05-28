import json
import paho.mqtt.client as mqtt
import hashlib
import random
import string
import sys

YELLOW = '\033[33m'
ENDC = '\033[m'


class Minerador():
    # Inicializar o minerador com uma tabela vazia de transações e assinar as filas sd/challenge e sd/result
    def __init__(self, broker, id_client, client):
        self.tabela = []
        self.endereco = broker 
        self.cliente = client
        self.id = id_client
        self.print_("Minerador iniciado")


    
    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.cliente.subscribe(fila)
        self.cliente.message_callback_add(fila, callback)

    def publicar(self, fila, mensagem):
        r = self.cliente.publish(fila, mensagem)



    def print_(self, texto):
        print(YELLOW,"Minerador ", self.id,ENDC, " | ", texto)

    # Definir uma função para gerar uma solução aleatória para um desafio
    def gerar_solucao(self, challenge):
        for i in range(0,sys.maxsize): 
            solucao = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            hash_solucao = hashlib.sha1(solucao.encode('utf-8')).digest()
            binario = bin(int.from_bytes(hash_solucao, 'big'))[2:]

            if binario[1:challenge+1] == '0'*challenge:
                return solucao

    # Definir uma função de callback para receber os desafios do controlador na fila sd/challenge
    def on_challenge(self, client, userdata, message):
        self.print_("Recebi um desafio!")
        dados = json.loads(message.payload.decode())
        transaction_id = dados["transaction_id"]
        challenge = dados["challenge"]
        while len(self.tabela) <= transaction_id:
            self.tabela.append([None, None, None, -1])
        self.tabela[transaction_id][0] = transaction_id
        self.tabela[transaction_id][1] = challenge
        solucao = self.gerar_solucao(challenge)
        self.tabela[transaction_id][2] = solucao
        mensagem = json.dumps({"client_id": self.id, "transaction_id": transaction_id,
                            "solution": solucao})
        self.print_("Enviando solução: {}".format(mensagem))
        self.publicar('sd/solution', mensagem)

        
    def on_connect(self, client, userdata, flags, rc):
        self.assinar('sd/challenge', self.on_challenge)
        self.assinar('sd/{}/result'.format(self.id), self.on_result)


    # Definir uma função de callback para receber os resultados do controlador na fila sd/result
    def on_result(self, client, userdata, message):
        dados = json.loads(message.payload.decode())
        self.print_("Recebi um resultado!")

        client_id = dados["client_id"]
        transaction_id = dados["transaction_id"]
        solucao = dados["solution"]
        result = dados["result"]
        if result == 1:
            self.print_("Solução aceita!")
            self.tabela[transaction_id][3] = client_id
        elif result == 0 and client_id == self.id:
            self.print_("Solução rejeitada!")
        else:
            self.print_("Solução rejeitada! Problema resolvido por: {}".format(client_id))
            self.tabela[transaction_id][3] = client_id
            self.tabela[transaction_id][2] = solucao
        	
        
            
    
    def start(self):
        
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        self.cliente.loop_start()


