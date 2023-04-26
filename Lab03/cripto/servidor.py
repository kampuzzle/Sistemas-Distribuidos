from concurrent import futures
import grpc
import mineracao_pb2
import mineracao_pb2_grpc
import hashlib
import uuid # para gerar identificadores únicos
import random # para gerar números aleatórios
import string


def generate_challenge():
    tamanho = random.randint(1, 6)
    letras = string.ascii_letters + string.digits
    return "".join(random.choice(letras) for i in range(tamanho))


#  Definindo a função que gera um desafio criptográfico
def generate_crypto_challenge(transaction_id):
    desafio = generate_challenge()
    challenge = hashlib.sha1(desafio.encode()).hexdigest()
    solution = 0
    winner = -1

    return (transaction_id, challenge, solution, winner)


class CryptoMiningServiceServicer(mineracao_pb2_grpc.apiServicer):

    def __init__(self):
        self.transactions = {}
        self.transactions[0] = generate_crypto_challenge(0)

    def getTransactionID(self, request, context):
        transaction_id = max(self.transactions.keys())
        return mineracao_pb2.intResult(result=transaction_id)

    def getChallenge(self, request):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(challenge=-1)
        elif self.transactions[request.transaction_id]['challenge'] is None:
            return mineracao_pb2.Transaction(challenge=0)
        else:
            return mineracao_pb2.Transaction(challenge=self.transactions[request.transaction_id]['challenge'])

    def getTransactionStatus(self, request):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        elif self.transactions[request.transaction_id]['solution'] is None:
            return mineracao_pb2.Transaction(winner=1)
        else:
            return mineracao_pb2.Transaction(winner=self.transactions[request.transaction_id]['winner'])

    def submitChallenge(self, request):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        elif self.transactions[request.transaction_id]['solution'] is not None:
            return mineracao_pb2.Transaction(winner=0)
        else:
            hash_object = hashlib.sha1(str(request.challenge).encode())
            hex_dig = hash_object.hexdigest()
            if hex_dig == self.transactions[request.transaction_id]['challenge']:
                self.transactions[request.transaction_id]['solution'] = request.solution
                self.transactions[request.transaction_id]['winner'] = request.winner
                return mineracao_pb2.Transaction(winner=2)
            else:
                return mineracao_pb2.Transaction(winner=1)

    def getWinner(self, request):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        else:
            return mineracao_pb2.Transaction(winner=self.transactions[request.transaction_id]['winner'])

    def getSolution(self, request):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.SolutionResult(status=-1)
        else:
            status = 0 if self.transactions[request.transaction_id]['solution'] else 1
            return mineracao_pb2.SolutionResult(status=status, solution=self.transactions[request.transaction_id]['solution'], challenge=self.transactions[request.transaction_id]['challenge'])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    mineracao_pb2_grpc.add_apiServicer_to_server(CryptoMisningServiceServicer(),
                                                 server)
    server.add_insecure_port('[::]:8080')
    server.start()
    
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
