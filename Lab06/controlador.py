import json
import paho.mqtt.client as mqtt
import hashlib
import random


class Controlador:
    def __init__(self, broker_address, broker_port):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.table = {}  # Tabela para armazenar os registros
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT")
        self.client.subscribe("sd/solution")  # Subscreve no tópico de soluções
        self.client.subscribe("sd/result")  # Subscreve no tópico de resultados

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        
        if topic == "sd/solution":
            self.process_solution(payload)
        elif topic == "sd/result":
            self.process_result(payload)

    def process_solution(self, payload):
        data = json.loads(payload)
        client_id = data["ClientID"]
        transaction_id = data["TransactionID"]
        solution = data["Solution"]

        if transaction_id in self.table:
            return

        challenge = self.table[transaction_id]["Challenge"]
        if self.verify_solution(challenge, solution):
            self.table[transaction_id]["Winner"] = client_id

    def process_result(self, payload):
        data = json.loads(payload)
        client_id = data["ClientID"]
        transaction_id = data["TransactionID"]
        result = data["Result"]
        print(f"Submissão de solução: ClientID={client_id}, TransactionID={transaction_id}, Result={result}")

    def generate_challenge(self):
        challenge = random.randint(1, 6)
        solution = self.calculate_solution(challenge)
        self.table[0] = {
            "Challenge": challenge,
            "Solution": solution,
            "Winner": -1
        }
        payload = json.dumps(self.table[0])
        self.client.publish("sd/challenge", payload)

    def calculate_solution(self, challenge):
        solution = hashlib.sha1(str(challenge).encode("utf-8")).hexdigest()
        return solution

    def verify_solution(self, challenge, solution):
        expected_solution = self.calculate_solution(challenge)
        return solution == expected_solution

    def print_table(self):
        print("Tabela:")
        print("TransactionID\tChallenge\tSolution\tWinner")
        for transaction_id, record in self.table.items():
            challenge = record["Challenge"]
            solution = record["Solution"]
            winner = record["Winner"]
            print(f"{transaction_id}\t\t{challenge}\t\t{solution}\t\t{winner}")

    def start(self):
        self.client.connect(self.broker_address, self.broker_port, 60)
        self.client.loop_start()
        self.generate_challenge()

        try:
            while True:
                self.print_menu()
                choice = input("Digite a opção desejada: ")
                self.process_choice(choice)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()
            print("Controlador desconectado")

    def print_menu(self):
        print("\nMenu:")
        print("1. newChallenge")
        print("2. exitController")

    def process_choice(self, choice):
        if choice == "1":
            self.new_challenge()
        elif choice == "2":
            self.exit_controller()
            exit()
        else:
            print("Opção inválida.")

    def new_challenge(self):
        self.generate_challenge()
        self.print_table()
        print("Aguardando resolução do desafio por algum minerador...")

    def exit_controller(self):
        self.client.unsubscribe("sd/result")
        print("Controlador desconectado e parou de assinar a fila sd/result.")



# Configurações do broker MQTT
broker_address = "broker.emqx.io"  # Endereço do broker MQTT (por exemplo, EMQX)
broker_port = 1883  # Porta do broker MQTT

# Cria uma instância do controlador
controlador = Controlador(broker_address, broker_port)

# Inicia o controlador
controlador.start()
