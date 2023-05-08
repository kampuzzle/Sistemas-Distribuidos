# Laboratório de Chamada de Procedimento Remoto 

## Compilação e Execução

dentro da pasta Lab03, navegue até a pasta cripto e execute o servidor e depois o cliente:

```
cd cripto
python3 servidor.py
python3 cliente.py
```

---

## Vídeo executando e mostrando uma análise

https://youtu.be/TSqqY8yZTt8

---

## Bibliotecas Utilizadas

* grpc: implementa funções para a comunicação de chamada de procedimento remoto (RPC) que permite que diferentes serviços se comuniquem uns com os outros de maneira eficiente e escalável.
* hashlib: fornece uma variedade de funções de hash seguras, que podem ser usadas para criptografia, armazenamento de senhas e autenticação de mensagens.
* threading: permite a criação e manipulação de threads de execução.

---

## Metodologia de implementação

Para implementar um serviço gRPC em Python, é necessário primeiro criar o arquivo proto e, em seguida, definir as funções que correspondem aos métodos especificados no arquivo. Portanto, seguimos uma abordagem de implementação de acordo com o arquivo proto, que nos foi previamente disponibilizada. Assim, criamos as funções de acordo com as especificações do arquivo, garantindo que a comunicação entre os sistemas seja realizada de forma consistente e eficiente.

Dessa forma, o primeiro arquivo que criamos foi o `servidor.py`, onde implementamos as funções definidas no service api do arquivo proto. 

Depois de termos o servidor pronto, fomos para a implementação do cliente. Criamos primeiro o menu descrito na especificação do laboratório, e fomos desenvolvendo funções para cada uma das opções disponíveis no menu.

Para criar os arquivos de `mineracao_pb2_grpc` e `mineracao_pb2`, executamos o grpc_tools dentro da pasta que contém o arquivo .proto, como especificado no laboratório.

---

## Servidor.py

Criamos servidor define seis funções para manipular transações de mineração: **getChallenge**, **getTransactionId**, **getTransactionStatus**, **submitChallenge**, **getWinner** e **getSolution**.

Ao executar o código, o servidor inicia e cria um desafio criptográfico inicial com a chave "0" usando a função `generate_crypto_challenge()`. Em seguida, o servidor cria uma nova thread para imprimir a tabela de transações a cada 5 segundos usando a função `print_table()`.

A função `getChallenge()` retorna o desafio criptográfico para uma transação específica com base em seu ID de transação. Se a transação ainda não existir ou se o desafio já tiver sido resolvido, a função retorna um valor de erro.

A função `getTransactionId()` retorna o ID da transação mais recente.

A função `getTransactionStatus()` retorna o status de uma transação específica com base em seu ID de transação. Se a transação ainda não existir ou se o desafio ainda não foi resolvido, a função retorna um valor de erro.

A função `submitChallenge()` recebe uma solução criptográfica para um desafio específico com base em seu ID de transação e cliente ID. Se a transação ainda não existir, ou se a solução já foi encontrada, a função retorna um valor de erro. Se a solução é válida, o servidor registra o cliente como o vencedor da transação e cria um novo desafio.

A função `getWinner()` retorna o ID do cliente vencedor para uma transação específica com base em seu ID de transação.

Por fim, a função `getSolution()` retorna a solução e o status (se a solução foi encontrada ou não) para uma transação específica com base em seu ID de transação. Se a transação ainda não existir, a função retorna um valor de erro.

---

## Cliente.py


A função `connect()` cria um canal gRPC seguro com o servidor e retorna um objeto stub que será utilizado para fazer as chamadas RPC.

A função `get_current_transaction(stub)` recebe o ID da transação atual do servidor, pelo parâmetro stub, e retorna o ID da transação atual.

A função `get_challenge(stub)` recebe o desafio atual do servidor, pelo parâmetro stub, solicita ao usuário que informe o ID da transação e imprime o desafio correspondente.

A função `get_transaction_status(stub)` recebe o status de uma transação do servidor, pelo parâmetro stub, solicita ao usuário que informe o ID da transação e imprime o status correspondente.

A função `get_winner(stub)` recebe o vencedor da transação do servidor, pelo parâmetro stub, solicita ao usuário que informe o ID da transação e imprime o vencedor correspondente.

A função `get_solution(stub)` recebe a solução de uma transação do servidor, pelo parâmetro stub,solicita ao usuário que informe o ID da transação e imprime a solução correspondente.

A função `mine(stub, client_unique_id)` minera a transação atual, recebendo pelo parâmetro o stub e o ID único do cliente, e chama a função mine_challenge em quatro threads diferentes para processamento paralelo.

A função `generate_random_solution(challenge)` gera uma solução aleatória para o desafio, recebendo como parâmetro o desafio para o qual a solução será gerada e retorna a solução gerada.

A função `mine_challenge(thread_id, challenge, client_unique_id, stub)` minera o desafio em uma thread específica, recebendo a ID da thread, o desafio a ser resolvido, o ID único do cliente e o stub. A função então divide o intervalo total de soluções em quatro partes iguais e processa a parte correspondente à thread. Se encontrar uma solução para o desafio, chama a função submitChallenge do servidor para submeter a solução.

A função `menu(stub)` exibe um menu de opções para o usuário, solicitando que o usuário escolha uma opção e chama a função correspondente. Se a opção escolhida for "0", encerra o programa.

---

## Resultados 

* Transaction ID = 0: 
> ---Winner solution:  47

> ---Time lapsed:  0.000000  seconds

* Transaction ID = 1:
> ---Winner solution:  830

>---Time lapsed:  0.002993  seconds

* Transaction ID = 2:
> ---Winner solution:  47

>---Time lapsed:  0.000000  seconds

* Transaction ID = 3:
> ---Winner solution:  461168602650089

>---Time lapsed:  5.675344  seconds

* Transaction ID = 4:
> ---Winner solution:  230584301240507

>---Time lapsed:  2.482456  seconds

* Transaction ID = 5:
> ---Winner solution:  230584301240507

>---Time lapsed:  1.652576  seconds

* Transaction ID = 6:
> ---Winner solution:  25762

>---Time lapsed:  0.074372  seconds

* Transaction ID = 7:
> ---Winner solution:  54

>---Time lapsed:  0.000000  seconds

* Transaction ID = 8:
> ---Winner solution:  47

>---Time lapsed:  0.000000  seconds 

* Transaction ID = 9:
> ---Winner solution:  1099

>---Time lapsed:  0.000000  seconds

* Transaction ID = 10:
> ---Winner solution:  47

>---Time lapsed:  0.000998  seconds


* Transaction ID = 11:
> ---Winner solution:  25762

>---Time lapsed:  0.120577  seconds

* Transaction ID = 12: 
> ---Winner solution:  230584301240507

>---Time lapsed:  1.716852  seconds

* Transaction ID = 13:
> ---Winner solution:  1099

>---Time lapsed:  0.003626  seconds

* Transaction ID = 14:
> ---Winner solution:  32030

>---Time lapsed:  0.066765  seconds

* Transaction ID = 15:
> ---Winner solution:  7

>---Time lapsed:  0.000000  seconds

* Transaction ID = 16:
> ---Winner solution:  47

>---Time lapsed:  0.000000  seconds

* Transaction ID = 17: 
> ---Winner solution:  47

>---Time lapsed:  0.000000  seconds

* Transaction ID = 18:
> ---Winner solution:  4913

>---Time lapsed:  0.000000  seconds

* Transaction ID = 19:
> ---Winner solution:  533968

>---Time lapsed:  2.821925  seconds

* Transaction ID = 20: 
> ---Winner solution:  461168602650089

>---Time lapsed:  6.880543  seconds

* Transaction ID = 21:
> ---Winner solution:  21

>---Time lapsed:  0.000000  seconds

* Transaction ID = 22:
> ---Winner solution:  54

>---Time lapsed:  0.000000  seconds

---

## Conclusão

Analisando os resultados acima, podemos ver que, para diferentes transações realizadas, cada uma com um ID único, tiveram um vencedor, que foi o cliente que conseguiu resolver o desafio criptográfico primeiro e submeteu a solução correta.

Além disso, foi registrado o tempo total gasto para resolver cada desafio. É interessante notar que o tempo varia de acordo com a complexidade do desafio e o poder de processamento do cliente. Desafios mais simples foram resolvidos em um tempo muito curto, enquanto desafios mais complexos exigiram um tempo maior para encontrar uma solução. Isso indica que o sistema é capaz de lidar com diferentes níveis de dificuldade dos desafios.

Vemos também que para alguns desafios o tempo registrado foi igual a zero segundos. Isso pode ocorrer quando o o desafio foi solucionado muito rapidamente, quase simultaneamente ao recebimento do desafio. Esses casos demonstram a eficiência do sistema em lidar com transações de mineração em tempo real.

É importante ressaltar que os resultados obtidos podem variar dependendo do ambiente de execução, como a capacidade de processamento dos clientes e a latência da rede. Em um ambiente com mais recursos computacionais e uma rede mais rápida, é provável que as transações sejam resolvidas mais rapidamente.

No geral, os resultados mostram que o sistema de mineração de transações criptográficas implementado é capaz de criar e resolver desafios criptográficos, registrar os vencedores corretamente e medir o tempo necessário para a solução. Isso demonstra a eficácia e a viabilidade do uso de chamadas de procedimento remoto (RPC) com gRPC para implementar um sistema distribuído de mineração de transações criptográficas.