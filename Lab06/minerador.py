import json
import paho.mqtt.client as mqtt
import hashlib
import random
from clienteMqtt import Cliente 



class Minerador(Cliente):
    # Inicializar o minerador com uma tabela vazia de transações e assinar as filas sd/challenge e sd/result
    def __init__(self):
        self.tabela = []
        self.assinar('sd/challenge', self.on_challenge)
        self.assinar('sd/result', self.on_result)
        print("Minerador iniciado")

    # Definir uma função para gerar uma solução aleatória para um desafio
    def gerar_solucao(self):
        return "".join(random.choices(string.ascii_letters + string.digits, k=10))

    # Definir uma função de callback para receber os desafios do controlador na fila sd/challenge
    def on_challenge(self, client, userdata, message):
        print("Recebi um desafio")
        dados = json.loads(message.payload.decode())
        transaction_id = dados["transaction_id"]
        challenge = dados["challenge"]
        while len(self.tabela) <= transaction_id:
            self.tabela.append([None, None, None, -1])
        self.tabela[transaction_id][0] = transaction_id
        self.tabela[transaction_id][1] = challenge
        solucao = self.gerar_solucao()
        self.tabela[transaction_id][2] = solucao
        mensagem = json.dumps({"client_id": self.id, "transaction_id": transaction_id,
                            "solution": solucao})
        self.publicar(sd_solution, mensagem)

    # Definir uma função de callback para receber os resultados do controlador na fila sd/result
    def on_result(self, client, userdata, message):
        dados = json.loads(message.payload.decode())
        client_id = dados["client_id"]
        transaction_id = dados["transaction_id"]
        solucao = dados["solution"]
        result = dados["result"]
        if transaction_id < len(self.tabela) and client_id == self.id:
            if result == 0:
                solucao = self.gerar_solucao()
                self.tabela[transaction_id][2] = solucao
                mensagem = json.dumps({"client_id": self.id,
                                    "transaction_id": transaction_id,
                                    "solution": solucao})
                self.publicar(sd_solution, mensagem)
            else:
                self.tabela[transaction_id][3] = client_id

