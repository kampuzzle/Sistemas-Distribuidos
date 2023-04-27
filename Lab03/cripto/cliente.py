import grpc
import mineracao_pb2
import mineracao_pb2_grpc
import threading
import random
import hashlib
import string

current_transaction = 0


def connect():
    channel = grpc.insecure_channel('localhost:8080')
    stub = mineracao_pb2_grpc.apiStub(channel)
    print("Stub created!")
    return stub


def get_current_transaction(stub):
    response = stub.getTransactionId(mineracao_pb2.void())
    print("Current transaction ID: ", response.result)
    return response.result


def get_challenge(stub):
    transaction_id = input("Enter transaction ID: ")
    response = stub.getChallenge(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    print("Challenge: ", response.result)


def get_transaction_status(stub):
    transaction_id = input("Enter transaction ID: ")
    response = stub.getTransactionStatus(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    print("Transaction status: ", response.result)


def get_winner(stub):
    
    transaction_id = input("Enter transaction ID: ")
    response = stub.getWinner(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    print("Winner: ", response.result)


def get_solution(stub):
    global current_transaction

    transaction_id = input("Enter transaction ID: ")
    response = stub.getSolution(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    print("Solution: ", response.result)


def mine(stub):
    current_transaction = stub.getTransactionId(mineracao_pb2.void()).result
    challenge = stub.getChallenge(mineracao_pb2.transactionId(transactionId=current_transaction)).result
    threads = []
    for i in range(4):  # 4 threads para processamento paralelo
        t = threading.Thread(target=mine_challenge, args=(i, challenge, stub))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def generate_random_solution(challenge):
    # generate a random string and apply it the hash function, until the hash matches the challenge
    solution = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    hash_solution = hashlib.sha1(solution.encode()).hexdigest()
    
    return hash_solution
    


def mine_challenge(thread_id, challenge, stub):

    current_transaction = stub.getTransactionId(mineracao_pb2.void()).result
    print("Thread ", thread_id, " started")
    
    while True:

        hash_solution = generate_random_solution(challenge)


        if hash_solution == challenge:
            break


    #  submeter solução ao servidor
    response = stub.submitChallenge(
        mineracao_pb2.challengeArgs(transactionId=int(current_transaction),
                                    clientId=thread_id,
                                    seed=solution))
    print("Thread ", thread_id, " server response: ", response.result)


def menu(stub):
    while True:
        print("Choose an option:")
        print("1. Get current transaction ID")
        print("2. Get challenge")
        print("3. Get transaction status")
        print("4. Get winner")
        print("5. Get solution")
        print("6. Mine")
        print("0. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            get_current_transaction(stub)
        elif choice == "2":
            get_challenge(stub)
        elif choice == "3":
            get_transaction_status(stub)
        elif choice == "4":
            get_winner(stub)
        elif choice == "5":
            get_solution(stub)
        elif choice == "6":
            mine(stub)
        elif choice == "0":
            break
        else:
            print("Invalid option!")

if __name__ == '__main__':
    stub = connect()

    current_transaction = get_current_transaction(stub)
    menu(stub)
