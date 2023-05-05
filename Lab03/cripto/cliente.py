import grpc
import mineracao_pb2
import mineracao_pb2_grpc
import threading
import random
import hashlib
import string
import os 
current_transaction = 0
already_solved = False


def connect():
    channel = grpc.insecure_channel('localhost:8080')
    stub = mineracao_pb2_grpc.apiStub(channel)
    print("Stub created!")
    return stub


def get_current_transaction(stub):
    response = stub.getTransactionId(mineracao_pb2.void())
    print("---Current transaction ID: ", response.result)
    return response.result


def get_challenge(stub):
    transaction_id = input("Enter transaction ID: ")
    response = stub.getChallenge(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    print("---Challenge: ", response.result)


def get_transaction_status(stub):
    transaction_id = input("Enter transaction ID: ")
    response = stub.getTransactionStatus(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    if response.result == 0:
        print("---Transaction solved")
    elif response.result == 1:
        print("---Transaction not solved")
    else:
        print("---Transaction does not exist")

def get_winner(stub):
    transaction_id = input("Enter transaction ID: ")
    response = stub.getWinner(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    # 0 there is no winner yet, -1 there is no transaction with this ID, else print the winner
    if response.result == 0:
        print("---There is no winner yet")
    elif response.result == -1:
        print("---Transaction does not exist")
    else:
        print("---Winner: ", response.result)


def get_solution(stub):
    global current_transaction

    transaction_id = input("Enter transaction ID: ")
    response = stub.getSolution(mineracao_pb2.transactionId(transactionId=int(transaction_id)))
    print("---Solution: ", response.result)


def mine(stub, client_unique_id):
    current_transaction = stub.getTransactionId(mineracao_pb2.void()).result
    challenge = stub.getChallenge(mineracao_pb2.transactionId(transactionId=current_transaction)).result
    threads = []
    for i in range(4):  # 4 threads para processamento paralelo
        t = threading.Thread(target=mine_challenge, args=(i, challenge,client_unique_id, stub))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def generate_random_solution(challenge):
    hash = hashlib.sha1(str(challenge).encode()).hexdigest()
    

def mine_challenge(thread_id, challenge, client_unique_id, stub):
    global already_solved
    already_solved = False

    
    # challenge is a int represent the amount of bits to be 0
    current_transaction = stub.getTransactionId(mineracao_pb2.void()).result
    print("---Thread ", thread_id, " started"	)
    whole_range = 922337203685477
    partition_range = int(whole_range / 4)
    thread_range = range(thread_id * partition_range, (thread_id + 1) * partition_range)

    

    for i in thread_range:
        if already_solved:
            return
        hash = hashlib.sha1((str(i)).encode()).digest()

        binary = bin(int.from_bytes(hash, byteorder='big'))[2:]

        if binary[1:challenge+1] == '0' * challenge:
            solution = str(i)

            if already_solved:
                return

            response = stub.submitChallenge(
            mineracao_pb2.challengeArgs(transactionId=int(current_transaction),
                                    clientId=client_unique_id,
                                    solution=solution)
            ) 
            #  print response
            if response.result == 2:
                print("---Thread ", thread_id, " finished, challenge was already solved")
            elif response.result == 1:
                print("---Thread ", thread_id, " finished, solution found! ")
                print("---Winner solution: ", solution	)

                c = True
            else:
                print("---Thread ", thread_id, " finished, solution was wrong")
            return
            
    print("---Thread ", thread_id, " finished, no solution found")
    return
    

   


def menu(stub):
    client_unique_id = random.randint(0, 1000000)
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
            mine(stub, client_unique_id)
        elif choice == "0":
            break
        else:
            print("---Invalid option!")

if __name__ == '__main__':
    stub = connect()

    current_transaction = get_current_transaction(stub)
    menu(stub)
