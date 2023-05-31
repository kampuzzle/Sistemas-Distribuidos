import json
import paho.mqtt.client as mqtt
import hashlib
import random
import time
import sys

BLUE = '\033[34m'

ENDC = '\033[m'




class Controlador():

    # Inicializar o controlador com uma tabela vazia de transações
    def __init__(self, broker, id, client):
        self.print_("Controlador iniciado")
        self.tabela = []

        self.endereco = broker
        self.cliente = client

        self.id = id
 

    def print_(self, texto):
        print(BLUE,"Controlador ",ENDC, " | ", texto)

    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.cliente.subscribe(fila)
        self.cliente.message_callback_add(fila, callback)

    def publicar(self, fila, mensagem):
        self.cliente.publish(fila, mensagem)

    # Definir uma função para gerar um novo desafio e publicá-lo na fila sd/challenge
    def novo_desafio(self):
        self.print_("Gerando novo desafio...")
        transaction_id = len(self.tabela)
        challenge = random.randint(15, 20)
        self.tabela.append([transaction_id, challenge, None, -1])
        mensagem = json.dumps({"transaction_id": transaction_id, "challenge": challenge})
        print("Desafio gerado: ", mensagem)
        self.publicar('sd/challenge', mensagem)
        self.print_("Desafio {} gerado!".format(transaction_id))

    # Definir uma função para verificar se uma solução é válida para um desafio
    def verificar_solucao(self, solucao, challenge):
        hash_solucao = hashlib.sha1(solucao.encode('utf-8')).digest()
        binario = bin(int.from_bytes(hash_solucao, 'big'))[2:]
        return binario[1:challenge+1] == '0'*challenge

    def on_connect(self, client, userdata, flags, rc):
        self.print_("Conectado ao broker!")
        self.assinar('sd/solution', self.on_solution)

       
    # Definir uma função de callback para receber as soluções dos mineradores na fila sd/solution
    def on_solution(self, client, userdata, message):
        self.print_("Recebi uma solução!")
        dados = json.loads(message.payload.decode())
        client_id = dados["client_id"]
        transaction_id = dados["transaction_id"]
        solucao = dados["solution"]

        if self.tabela[transaction_id][3] != -1:
            mensagem = json.dumps({"client_id": self.tabela[transaction_id][3], "transaction_id": transaction_id,
                                "solution": solucao, "result": 0})
            self.publicar(f'sd/{client_id}/result', mensagem)
            return

        if transaction_id < len(self.tabela) and self.tabela[transaction_id][3] == -1:
            challenge = self.tabela[transaction_id][1]
            if self.verificar_solucao(solucao, challenge):
                self.tabela[transaction_id][2] = solucao
                self.tabela[transaction_id][3] = client_id
                result = 1
                self.print_(texto=f"Minerador {client_id} resolveu o desafio {transaction_id}!"	)
            else:
                result = 0
                
                
            
            mensagem = json.dumps({"client_id": client_id, "transaction_id": transaction_id,
                                "solution": solucao, "result": result})
            self.publicar(f'sd/{client_id}/result', mensagem)


    def loop(self):
        while True:
            time.sleep(4)
            sys.stdout.flush()
            a = input("Digite 'n' para gerar um novo desafio, 'e' para encerrar: ")
            if a == 'e':
                break
            if a != 'n':
                self.print_("Comando inválido!")
                continue
            


            self.novo_desafio()

            while self.tabela[-1][3] == -1:
                self.print_(texto="Esperando por uma solução...")
                time.sleep(1)

            self.print_("Desafio resolvido!")

    def start(self):
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        self.cliente.loop_start()

        self.loop()
