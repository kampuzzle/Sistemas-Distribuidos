import json
import paho.mqtt.client as mqtt
import hashlib
import random
import string
import sys
from cryptography.hazmat.primitives import serialization
import binascii
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


YELLOW = '\033[33m'
ENDC = '\033[m'

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

    public_key = binascii.unhexlify(public_key)

    public_key = load_pem_public_key(public_key)
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

class Minerador():
    # Inicializar o minerador com uma tabela vazia de transações e assinar as filas sd/challenge e sd/result
    def __init__(self, broker, id_client, client, node_id, clients_on_network, private_key, controller_key):
        self.tabela = []
        self.endereco = broker 
        self.cliente = client
        self.node_id = id_client
        self.controller_key = controller_key
        self.node_id = node_id
        self.clients_on_network = clients_on_network
        self.private_key = private_key

        self.print_("Minerador iniciado")




    
    def assinar(self, fila, callback):
        self.print_("Assinando a fila " + fila)
        self.cliente.subscribe(fila)
        self.cliente.message_callback_add(fila, callback)

    def publicar(self, fila, mensagem):
        r = self.cliente.publish(fila, mensagem)



    def print_(self, texto):
        print(YELLOW,"Minerador ", self.node_id,ENDC, " | ", texto)

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


        dados = json.loads(message.payload.decode('utf-8'))

        # Verificando a assinatura
        signature = dados["signature"]
        challenge = dados["challenge"]

        public_key = self.clients_on_network[dados["client_id"]]

        if not verificar_assinatura(public_key, bytes(challenge), binascii.unhexlify(signature)):
            self.print_("Assinatura inválida!")
            return

        transaction_id = dados["transaction_id"]
        while len(self.tabela) <= transaction_id:
            self.tabela.append([None, None, None, -1])
        self.tabela[transaction_id][0] = transaction_id
        self.tabela[transaction_id][1] = challenge
        solucao = self.gerar_solucao(challenge)
        self.tabela[transaction_id][2] = solucao
        signature = assinar_mensagem(self.private_key, solucao.encode())
        mensagem = json.dumps({"client_id": self.node_id, "transaction_id": transaction_id,
                            "solution": solucao, "signature":signature.hex()})
        self.print_("Enviando solução: {}".format(mensagem))
        self.publicar('sd/solution', mensagem)

        
    def on_connect(self, client, userdata, flags, rc):
        self.assinar('sd/challenge', self.on_challenge)
        self.assinar('sd/{}/result'.format(self.node_id), self.on_result)


    # Definir uma função de callback para receber os resultados do controlador na fila sd/result
    def on_result(self, client, userdata, message):
        dados = json.loads(message.payload.decode('utf-8'))
        self.print_("Recebi um resultado!")

        # Verificando a assinatura
        signature = dados["signature"]
        solucao = dados["solution"]
        result = dados["result"]

    
        if not verificar_assinatura(self.controller_key, bytes(result), binascii.unhexlify(signature)):
            self.print_("Assinatura inválida!")
            return

        client_id = dados["client_id"]
        transaction_id = dados["transaction_id"]
       
        if result == 1:
            self.print_("Solução aceita!")
            self.tabela[transaction_id][3] = client_id
        elif result == 0 and client_id == self.node_id:
            self.print_("Solução rejeitada!")
        else:
            self.print_("Solução rejeitada! Problema resolvido por: {}".format(client_id))
            self.tabela[transaction_id][3] = client_id
            self.tabela[transaction_id][2] = solucao
        	
        
            
    
    def start(self):
        
        self.cliente.on_connect = self.on_connect
        self.cliente.connect(self.endereco)
        self.cliente.loop_start()


