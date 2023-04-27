from concurrent import futures
import grpc
import mineracao_pb2
import mineracao_pb2_grpc
import hashlib
import uuid # para gerar identificadores únicos
import random # para gerar números aleatórios
import string


def generate_challenge():
    return random.randint(1, 6)
   

#  Definindo a função que gera um desafio criptográfico
def generate_crypto_challenge(transactionId):
    challenge = generate_challenge()
    print("Challenge: ", challenge)
    solution = 0
    winner = -1

    return {'challenge': challenge, 'solution': solution, 'winner': winner}


class CryptoMiningServiceServicer(mineracao_pb2_grpc.apiServicer):

    def __init__(self):
        self.transactions = {}
        self.transactions[0] = generate_crypto_challenge(0)


    def getChallenge(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.intResult(result=-1)
        elif self.transactions[request.transactionId]['challenge'] is None:
            return mineracao_pb2.intResult(result=0)
        else:
            print("Challenge: ", self.transactions[request.transactionId]['challenge'])
            return mineracao_pb2.intResult(result=self.transactions[request.transactionId]['challenge'])

    
    def getTransactionId(self, request, context):
        transaction_id = max(self.transactions.keys())
        return mineracao_pb2.intResult(result=transaction_id)


    def getTransactionStatus(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        elif self.transactions[request.transactionId]['solution'] is None:
            return mineracao_pb2.Transaction(winner=1)
        else:
            return mineracao_pb2.Transaction(winner=self.transactions[request.transactionId]['winner'])

    def submitChallenge(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        elif self.transactions[request.transactionId]['solution'] is not None:
            return mineracao_pb2.Transaction(winner=0)
        else:
            hash_object = hashlib.sha1(str(request.challenge).encode())
            hex_dig = hash_object.hexdigest()
            if hex_dig == self.transactions[request.transactionId]['challenge']:
                self.transactions[request.transactionId]['solution'] = request.solution
                self.transactions[request.transactionId]['winner'] = request.winner
                return mineracao_pb2.Transaction(winner=2)
            else:
                return mineracao_pb2.Transaction(winner=1)

    def getWinner(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        else:
            return mineracao_pb2.Transaction(winner=self.transactions[request.transactionId]['winner'])

    def getSolution(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.SolutionResult(status=-1)
        else:
            status = 0 if self.transactions[request.transactionId]['solution'] else 1
            return mineracao_pb2.SolutionResult(status=status, solution=self.transactions[request.transactionId]['solution'], challenge=self.transactions[request.transactionId]['challenge'])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    mineracao_pb2_grpc.add_apiServicer_to_server(CryptoMiningServiceServicer(),
                                                 server)
    server.add_insecure_port('[::]:8080')
    server.start()
    
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
