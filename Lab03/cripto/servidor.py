from concurrent import futures
import grpc
import mineracao_pb2
import mineracao_pb2_grpc
import hashlib
import uuid # para gerar identificadores únicos
import random # para gerar números aleatórios
import string
import threading
import time

def generate_challenge():
    return random.randint(1, 32)
   

#  Definindo a função que gera um desafio criptográfico
def generate_crypto_challenge(transactionId):
    challenge = generate_challenge()
    solution = None
    winner = -1

    return {'challenge': challenge, 'solution': solution, 'winner': winner}


class CryptoMiningServiceServicer(mineracao_pb2_grpc.apiServicer):

    def __init__(self):
        self.transactions = {}
        self.transactions[0] = generate_crypto_challenge(0)
        print("Initial challenge: ", self.transactions[0]['challenge'])
        
        thread = threading.Thread(target=self.print_table, args=())
        thread.daemon = True
        thread.start()



    def print_table(self):
        #print table every 5 seconds
        while True:
            print("Transaction ID | Challenge | Solution | Winner")
            for transaction_id in self.transactions:
                print("{} | {} | {} | {}".format(transaction_id, self.transactions[transaction_id]['challenge'], self.transactions[transaction_id]['solution'], self.transactions[transaction_id]['winner']))
            print("------------------------------------------------")
            time.sleep(5)
 
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
            return mineracao_pb2.intResult(result=-1)
        elif self.transactions[request.transactionId]['solution'] is None:
            return mineracao_pb2.intResult(result=1)
        else:
            return mineracao_pb2.intResult(result=self.transactions[request.transactionId]['winner'])

    def submitChallenge(self, request, context):
        

        challenge = self.transactions[request.transactionId]['challenge']
        if request.transactionId not in self.transactions:
            return mineracao_pb2.intResult(result=-1)
        elif self.transactions[request.transactionId]['solution'] is not None:
            return mineracao_pb2.intResult(result=2)
        else:
            print("Solution submitted: ", request.solution	)
            hash = hashlib.sha1(str(request.solution).encode()).digest()
            binary = bin(int.from_bytes(hash, byteorder='big'))[2:]

            if binary[1:challenge+1] == '0' * challenge:
                # if winner -1 -> no winner
                if self.transactions[request.transactionId]['winner'] == -1:
                        
                    self.transactions[request.transactionId]['solution'] = request.solution
                    self.transactions[request.transactionId]['winner'] = request.clientId
                    print("Winner for challenge {}: {}".format(challenge, request.clientId))
                    print("Solution: ", self.transactions[request.transactionId]['solution'])

                    # generate new challenge
                    self.transactions[request.transactionId + 1] = generate_crypto_challenge(request.transactionId + 1)
                    print("New challenge: ", self.transactions[request.transactionId + 1]['challenge'])

                    return mineracao_pb2.intResult(result=1)
                else :
                    return mineracao_pb2.intResult(result=2)
            else:
                return mineracao_pb2.intResult(result=0)

    def getWinner(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.intResult(result=-1)
        else:
            return mineracao_pb2.intResult(result=self.transactions[request.transactionId]['winner'])

    def getSolution(self, request, context):
        if request.transactionId not in self.transactions:
            return mineracao_pb2.structResult(status=-1)
        else:
            status = 0 if self.transactions[request.transactionId]['solution'] else 1
            return mineracao_pb2.structResult(status=status, solution=self.transactions[request.transactionId]['solution'], challenge=self.transactions[request.transactionId]['challenge'])


def serve():
    print("Starting server...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    mineracao_pb2_grpc.add_apiServicer_to_server(CryptoMiningServiceServicer(),
                                                 server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Listening on port 8080.")


    
    server.wait_for_termination()



if __name__ == '__main__':
    serve()
