import grpc
import grpcCalc_pb2
import grpcCalc_pb2_grpc
import pybreaker

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)
@breaker

def run(client, n):
    if n == '1':
        print('Adição:')
        x = int(input('Entre com o primeiro número: '))
        y = int(input('Entre com o segundo número: '))
        # raise pybreaker.CircuitBreakerError
        res = client.add(grpcCalc_pb2.args(numOne=x, numTwo=y))
        print(res.num)
    elif n == '2':
        print('Subtração:')
        x = int(input('Entre com o primeiro número: '))
        y = int(input('Entre com o segundo número: '))
        res = client.sub(grpcCalc_pb2.args(numOne=x, numTwo=y))
        # tme.sleep(5)
        print(res.num)
    elif n == '3':
        print('Multiplicação:')
        x = int(input('Entre com o primeiro número: '))
        y = int(input('Entre com o segundo número: '))
        res = client.mul(grpcCalc_pb2.args(numOne=x, numTwo=y))
        print(res.num)
    elif n == '4':
        print('Divisão:')
        x = int(input('Entre com o primeiro número: '))
        y = int(input('Entre com o segundo número: '))
        res = client.div(grpcCalc_pb2.args(numOne=x, numTwo=y))
        print(res.num)
    elif n == '5':
        print('Fim.')
        exit()
    else:
        print('Entrada Inválida,')

@breaker
def connect():
    channel = grpc.insecure_channel('localhost:8080')
    client = grpcCalc_pb2_grpc.apiStub(channel)
    while True:
        print('Escolha:')
        print('1 para Adição,')
        print('2 para Subtração,')
        print('3 para Multiplicação,')
        print('4 para Divisão')
        print('5 para Finalizar')
        print()
        
        n = input('Enter your choice: ')
        
        try:
            running = run(client, n)
            # print(running)
        except pybreaker.CircuitBreakerError:
            print(pybreaker.CircuitBreakerError)


if __name__ == '__main__':
    connect()

