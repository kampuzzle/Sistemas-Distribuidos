# Publish Subscribe com MQTT

## Instruções para execução

Execute o código main.py, acrescente o argumento N que rerpresenta o número de clientes que irão participar. 

Por padrão, o código se conecta ao broker "broker.emqx.io", mas pode ser alterado se, quando executado, o main.py receber um segundo argumento que representa o endereço do broker. 


O código main simula uma situacao em que N clientes se inscrevem e divide cada um em threads. Cada Cliente irá se manifestar no terminal, sendo diferenciado pelos ids e cores do terminal. 

Quanto todos os clientes se conectarem, um menu irá perguntar se deseja encerrar o programa ou gerar um novo desafio. Digite 'e' para encerrar o programa ou 'n' para gerar um novo desafio.


## Descrição da implementação

O código main.py se conecta a um broker e a N clientes. Cada cliente é dividido em uma thread. Cada cliente se inscreve em um tópico e publica mensagens nesse tópico. O broker recebe as mensagens e as distribui para os clientes inscritos no tópico.

A classe Cliente implementa as funções que irão coordenar a eleição. Quando n clients forem iniciados, a eleição começa e, através de votação aleatória, um líder é escolhido. O líder é responsável por enviar mensagens de controle para os outros clientes utilizando as funções de controle implementadas na classe Controlador. Por fim, o líder é responsável por enviar os desafios criptográficos para os outros clientes, alimentando uma fila no mqtt, que será consumida pelos outros clientes. Estes que irão utilizar as funções implementadas pela classe de Minerador.  

O Controlador irá, em looping, gerar um desafio 



## Testes 

Testando o código com 3 clientes, nota-se 