import json
import paho.mqtt.client as mqtt
import hashlib
import random
from clienteMqtt import Cliente 
import time

BLUE = '\033[34m'

ENDC = '\033[m'


class Controlador(Cliente):

    # Inicializar o controlador com uma tabela vazia de transações
    def __init__(self):
        self.print_("Controlador iniciado")
        self.tabela = []

    def print_(self, texto):
        print(BLUE,"Controlador ",ENDC, " | ", texto)

    # Definir uma função para gerar um novo desafio e publicá-lo na fila sd/challenge
    def novo_desafio(self):
        self.print_("Gerando novo desafio...")
        transaction_id = len(self.tabela)
        challenge = random.randint(1, 6)
        self.tabela.append([transaction_id, challenge, None, -1])
        mensagem = json.dumps({"transaction_id": transaction_id, "challenge": challenge})
        self.publicar('sd/challenge', mensagem)
        self.print_("Desafio {} gerado!".format(transaction_id))

    # Definir uma função para verificar se uma solução é válida para um desafio
    def verificar_solucao(self, solucao, challenge):
        hash = hashlib.sha1(solucao.encode()).hexdigest()
        return hash.endswith("0" * challenge)

    # Definir uma função de callback para receber as soluções dos mineradores na fila sd/solution
    def on_solution(self, client, userdata, message):
        self.print_("Recebi uma solução!")
        dados = json.loads(message.payload.decode())
        client_id = dados["client_id"]
        transaction_id = dados["transaction_id"]
        solucao = dados["solution"]
        if transaction_id < len(self.tabela) and self.tabela[transaction_id][3] == -1:
            challenge = self.tabela[transaction_id][1]
            if self.verificar_solucao(solucao, challenge):
                self.tabela[transaction_id][2] = solucao
                self.tabela[transaction_id][3] = client_id
                result = 1
            else:
                result = 0
            mensagem = json.dumps({"client_id": client_id, "transaction_id": transaction_id,
                                "solution": solucao, "result": result})
            self.publicar('sd/result', mensagem)

    def loop(self):
        # self.client.message_callback_add('sd/solution', self.on_solution)
        self.client.loop_start()
        while True:
            self.novo_desafio()
            time.sleep(10)
