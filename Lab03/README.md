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


---

## Conclusão
