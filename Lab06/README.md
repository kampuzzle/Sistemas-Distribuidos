# Publish Subscribe com MQTT

## Instruções para execução

Execute o código main.py, acrescente o argumento N que representa o número de clientes que irão participar. 

Por padrão, o código se conecta ao broker "broker.emqx.io", mas pode ser alterado se, quando executado, o main.py receber um segundo argumento que representa o endereço do broker. 

O código main simula uma situacao em que N clientes se inscrevem e divide cada um em threads. Cada Cliente irá se manifestar no terminal, sendo diferenciado pelos ids e cores do terminal. 

Quanto todos os clientes se conectarem, um menu irá perguntar se deseja encerrar o programa ou gerar um novo desafio. Digite 'e' para encerrar o programa ou 'n' para gerar um novo desafio.

---

## Vídeo executando

https://drive.google.com/file/d/13QDhC5L9TKvk6kZA-sMeoc4HGJ5Pg2oa/view?usp=sharing

---

## Descrição da implementação

O código main.py se conecta a um broker e a N clientes. Cada cliente é dividido em uma thread. Cada cliente se inscreve em um tópico e publica mensagens nesse tópico. O broker recebe as mensagens e as distribui para os clientes inscritos no tópico.

A classe Cliente implementa as funções que irão coordenar a eleição. Quando n clients forem iniciados, a eleição começa e, através de votação aleatória, um líder é escolhido. O líder é responsável por enviar mensagens de controle para os outros clientes utilizando as funções de controle implementadas na classe Controlador. Por fim, o líder é responsável por enviar os desafios criptográficos para os outros clientes, alimentando uma fila no mqtt, que será consumida pelos outros clientes. Estes que irão utilizar as funções implementadas pela classe de Minerador.  

O Controlador irá, em looping, gerar um sistema de desafios em que os mineradores tentam resolver os desafios enviando soluções para o controlador. O controlador verifica se as soluções são válidas e atribui o desafio resolvido a um minerador específico. As funções disponíveis na classe são responsáveis por iniciar a conexão com o broker MQTT, iniciar e verificar desafios, essa verificação é feita utilizando a função de hash SHA-1.

Já o Minerador recebe desafios do controlador, gera soluções para esses desafios e envia as soluções de volta para o controlador. O minerador também recebe os resultados do controlador e atualiza sua tabela de transações com as informações relevantes. Ele gera uma solução aleatória para um desafio recebido, utilizando caracteres minúsculos aleatórios e a função de hash SHA-1. O minerador também recebe a informação se sua solução enviada foi aceita ou não. Se o resultado for 1, significa que a solução foi aceita pelo controlador e o minerador atualiza sua tabela de transações com o ID do cliente que resolveu o desafio. Se o resultado for 0 e o ID do cliente for igual ao ID do minerador, significa que a solução foi rejeitada. Caso contrário, significa que a solução foi resolvida por outro cliente e o minerador atualiza sua tabela com o ID do cliente e a solução correta.

---

## Testes 

Testando o código com n = 3, temos a criação de 3 clientes diferentes, mostrados abaixo:
* cliente  36804
* cliente  3952
* cliente  26094

Para o desafio 0, o minerador **3952** resolveu o desafio, achando a solução = `{"client_id": 3952, "transaction_id": 0, "solution": "lpcqozdpqb"}`. 

Para o desafio 1, o minerador **3952** resolveu o desafio, achando a solução = `{"client_id": 3952, "transaction_id": 1, "solution": "zlaffpqedw"}`.

Para o desafio 2, o minerador **26094** resolveu o desafio, achando a solução = `{"client_id": 26094, "transaction_id": 2, "solution": "vssftizohr"}`. 

Testando o código com n = 5, temos a criação de 5 clientes diferentes, mostrados abaixo:

* cliente  53061
* cliente  36084
* cliente  21170
* cliente  57700
* cliente  1483

Para o desafio 0, o minerador **21170** resolveu o desafio, achando a solução = `{"client_id": 21170, "transaction_id": 0, "solution": "fwxxzdvipr"}`

Para o desafio 1, o minerador **1483** resolveu o desafio, achando a solução = `{"client_id": 1483, "transaction_id": 1, "solution": "pbvhezqvgu"}`

Para o desafio 2, o minerador **36084** resolveu o desafio, achando a solução = `{"client_id": 36084, "transaction_id": 2, "solution": "rdsnvazauk"}`


Testando o código com n = 10, temos a criação de 10 clientes diferentes, mostrados abaixo:
* cliente  21953
* cliente  29742
* cliente  29869
* cliente  22475
* cliente  17637
* cliente  44490
* cliente  49074
* cliente  14931
* cliente  20338
* cliente  40194

Para o desafio 0, o minerador **17637** resolveu o desafio, achando a solução = `{"client_id": 17637, "transaction_id": 0, "solution": "njsnvjuojk"}`.

Para o desafio 1, o minerador **44490** resolveu o desafio, achando a solução = `{"client_id": 44490, "transaction_id": 1, "solution": "wxpjymqbdp"}`.

Para o desafio 2, o minerador **22475** resolveu o desafio, achando a solução =`{"client_id": 22475, "transaction_id": 2, "solution": "wyrfojgfbv"}`.

Para o desafio 2, o minerador **49074** resolveu o desafio, com a solução = `{"client_id": 49074, "transaction_id": 3, "solution": "kgtbyiozgx"}`