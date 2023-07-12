import json
import paho.mqtt.client as mqtt
import hashlib
import random
import time
import sys

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


BLUE = '\033[34m'

ENDC = '\033[m'

PINK = '\033[35m'

def assinar_mensagem(private_key, message):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verificar_assinatura(public_key, message, signature):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

class Controlador():

    # Inicializar o controlador com uma tabela vazia de transações
    def __init__(self, broker, id, client, node_id, clients_on_network, private_key):
        self.print_("Controlador iniciado")
        self.tabela = []

        self.endereco = broker
        self.cliente = client

        self.id = id

        self.node_id = node_id
        self.clients_on_network = clients_on_network
        self.private_key = private_key


 

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
        signature = assinar_mensagem(self.private_key, bytes(str(challenge)))
        mensagem = json.dumps({"transaction_id": transaction_id, "challenge": str(challenge), "signature": signature.hex()})
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

        signature = dados["signature"]
        message = dados["solution"]

        public_key = self.clients_on_network[dados["client_id"]]

        # Verificando assinatura
        if not verificar_assinatura(public_key, message, binascii.unhexlify(signature)):
            self.print_("Assinatura inválida!")
            return

        client_id = dados["client_id"]
        transaction_id = dados["transaction_id"]
        solucao = dados["solution"]

        signature = assinar_mensagem(self.private_key, bytes(str(solucao)))

        if self.tabela[transaction_id][3] != -1:
            mensagem = json.dumps({"client_id": self.tabela[transaction_id][3], "transaction_id": transaction_id,
                                "solution": solucao, "result": 0, "signature": signature.hex()})
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
                
            signature = assinar_mensagem(self.private_key, bytes(str(solucao)))    
            
            mensagem = json.dumps({"client_id": client_id, "transaction_id": transaction_id,
                                "solution": solucao, "result": result, "signature": signature.hex()})
            self.publicar(f'sd/{client_id}/result', mensagem)


    def loop(self):
        while True:
            time.sleep(4)
            sys.stdout.flush()
            a = input(PINK + "Digite 'n' para gerar um novo desafio, 'e' para encerrar: " + ENDC)
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
