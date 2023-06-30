# Trabalho T1 – Implementação de Aprendizado Federado

## Instruções para execução do código 

Requisitos: Docker e Docker Compose 

Para executar o código, basta rodar o shell script up.sh, que irá criar o container do do MQTT e, em seguida, o código do trabalho.

```bash
./up.sh
```

## Vídeo executando e mostrando uma análise

https://youtu.be/5E5stN3CJ54

---

## Metodologia de implementação

A aplicação foi desenvolida utilizando um servidor MQTT para o controle da fila de mensagens, onde cada cliente, representado por um diferente processo, atua como um peer da rede. O servidor MQTT é responsável por receber as mensagens dos clientes e distribuir para os outros clientes, que irão processar as mensagens e enviar as respostas para o servidor.

O código funciona através da sincronização dos estados dos clientes por meio de publicações em filas. 

### clienteMqtt.py
O cliente MQTT é responsável por se conectar ao servidor MQTT e publicar as mensagens nas filas. Ele também é responsável por se inscrever nas filas para receber as mensagens de outros clientes.

Além disso, ele atua no controle da eleição, para, assim, definir quais serão os treinadores e qual será o controlador. 


### treinador.py

O treinador recebe a ordem do controlador para começar o treinamento, e então ele começa a treinar o modelo, enviando as atualizações para o controlador. Enviando, por MQTT, os pesos do modelo e a acurácia do modelo treinado. 


### controlador.py

O controlador é responsável por receber as atualizações dos treinadores, e então, atualizar o modelo global, que é a média federada dos pesos dos modelos treinados pelos treinadores. Ele também é responsável por enviar os pesos do modelo global para os treinadores, para que eles possam treinar com os pesos atualizados.

Ao final da meta de acurácia, o controlador envia uma mensagem para os treinadores, para que eles parem de treinar e enviem a acurácia final do modelo treinado. Isso também ocorre se o número de rounds for atingido, ou se o controlador receber uma mensagem de parada de treinamento de um dos treinadores.

---

## Resultados 

Temos dois exemplos para mostrar os resultados, o clients_history_1 e clients_history_2.

Nesse treinamento, utilizamos quatro clientes, a seguir estarão os gráficos da acurácia de cada cliente de acordo com os rounds:

Cliente 1:

![Gráfico do cliente 1](clients_history_1/client_1_clients_history_1.png)

Cliente 2:

![Gráfico do cliente 2](clients_history_1/client_2_clients_history_1.png)

Cliente 3:

![Gráfico do cliente 3](clients_history_1/client_3_clients_history_1.png)

Nesse cliente 3, removemos ele de 5 rounds, para mostrar que é possível tirar um cliente e inserí-lo novamente.

Cliente 4:

![Gráfico do cliente 4](clients_history_1/client_4_clients_history_1.png)

Como podemos ver em todos os gráficos, a acurácia vai aumentando com a iteração dos rounds, porém não necessariamente com todos os rounds tendo mais acurácia que o anterior. Como podemos ver, por exemplo, no cliente 1, em diversos pontos a acurácia diminui para aumentar novamente, mas no geral ela está muito maior que nos primeiros rounds.

Modelo Global:

![Modelo global](clients_history_1/global_model_clients_history_1.png)

Aqui, podemos ver a acurácia do modelo global crescendo rapidamente, porém a partir do round 7, a acurácia não tem um aumento significativo, se tornando um valor repetitivo com vários rounds.

Acurácia de todos os clientes:

![Todos os clientes](clients_history_1/all_clients_clients_history_1.png)

Na comparação de acurácia entre os clientes, podemos analisar que eles vão tendo resultados parecidos com o avanço dos rounds, sem muita diferença entre as acurácias, com exceção do cliente 3, que foi removido dos treinamentos por alguns rounds. Porem, podemos ver que removê-lo faz diferença apenas caso ele não volte aos treinamentos, mas mesmo com rounds a menos, ele chegou nas mesmas acurácias que os outros clientes.

Em seguida, fizemos o mesmo teste com 5 clientes, e os resultados podem ser vistos a seguir:

Cliente 1:

![Gráfico do cliente 1](clients_history_2/client_1_clients_history_2.png)

No cliente 1, testamos conecta-lo apenas no round 3, para avaliar se o momento que ele começa o treinamento afeta a acurácia, porém podemos ver que não houve diferença, e ele rapidamente estava com uma ótima acurácia. Isso acontece porque o cliente que se conecta recebe os pesos globais que é a media federada dos pesos que foram treinados por outros clientes, assim, um novo cliente já começa com um modelo bem treinado. 

Cliente 2:

![Gráfico do cliente 2](clients_history_2/client_2_clients_history_2.png)

Cliente 3:

![Gráfico do cliente 3](clients_history_2/client_3_clients_history_2.png)

Cliente 4:

![Gráfico do cliente 4](clients_history_2/client_4_clients_history_2.png)

Cliente 5:

![Gráfico do cliente 5](clients_history_2/client_5_clients_history_2.png)

T:odos os clientes:

![Todos os clientes](clients_history_2/all_clients_clients_history_2.png)

Neste último gráfico, podemos então ter certeza que, para uma grande quantidade de rounds, não importa se um cliente começa o treinamento após outros, que rapidamente ele chegará na acurácia parecida aos outros clientes. 

---

## Conclusão

Por fim, podemos concluir que, a acurácia em algum momento se estagnará, e não terá um avanço grande mesmo com uma quantidade grande de rounds, tornando o treinamento por muitos rounds desnecessário. Também conseguimos ver pelos gráficos, que remover um cliente, ou fazer ele iniciar tardiamente não afeta seu resultado, com ele chegando nos mesmos resultados ou superiores que os outros clientes.

Portanto, o treinamento federado funcionou como o esperado, ótimo para obter as acurácias, com os valores chegando muito perto de 0.99, que era nosso target accuracy. 
