from concurrent import futures
import grpc
import mineracao_pb2
import mineracao_pb2_grpc
import hashlib


class CryptoMiningServiceServicer(mineracao_pb2_grpc.apiServicer):

    def __init__(self):
        self.transactions = {}

    def getTransactionID(self, request, context):
        transaction_id = max(self.transactions.keys()) + 1 if self.transactions else 1
        self.transactions[transaction_id] = {'challenge': None, 'solution': None, 'winner': None}
        return mineracao_pb2.Transaction(transaction_id=transaction_id)

    def getChallenge(self, request, context):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(challenge=-1)
        elif self.transactions[request.transaction_id]['challenge'] is None:
            return mineracao_pb2.Transaction(challenge=0)
        else:
            return mineracao_pb2.Transaction(challenge=self.transactions[request.transaction_id]['challenge'])

    def getTransactionStatus(self, request, context):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        elif self.transactions[request.transaction_id]['solution'] is None:
            return mineracao_pb2.Transaction(winner=1)
        else:
            return mineracao_pb2.Transaction(winner=self.transactions[request.transaction_id]['winner'])

    def submitChallenge(self, request, context):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        elif self.transactions[request.transaction_id]['solution'] is not None:
            return mineracao_pb2.Transaction(winner=0)
        else:
            hash_object = hashlib.sha1(str(request.challenge).encode())
            hex_dig = hash_object.hexdigest()
            if hex_dig[:5] == '00000':
                self.transactions[request.transaction_id]['solution'] = request.solution
                self.transactions[request.transaction_id]['winner'] = request.winner
                return mineracao_pb2.Transaction(winner=2)
            else:
                return mineracao_pb2.Transaction(winner=1)

    def getWinner(self, request, context):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.Transaction(winner=-1)
        else:
            return mineracao_pb2.Transaction(winner=self.transactions[request.transaction_id]['winner'])

    def getSolution(self, request, context):
        if request.transaction_id not in self.transactions:
            return mineracao_pb2.SolutionResult(status=-1)
        else:
            status = 0 if self.transactions[request.transaction_id]['solution'] else 1
            return mineracao_pb2.SolutionResult(status=status, solution=self.transactions[request.transaction_id]['solution'], challenge=self.transactions[request.transaction_id]['challenge'])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mineracao_pb2_grpc.add_apiServicer_to_server(CryptoMiningServiceServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
