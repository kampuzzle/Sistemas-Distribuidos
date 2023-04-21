# Laboratório de Aprendizado Federado  - Atividade 2

## Compilação e Execução

Dentro da pasta Lab02/Atividade2, execute o seguinte comando:

```
./run.sh
```

Caso encontre algum erro de permissão, rode o comando abaixo para dar permissão total ao script e tente novamente

```
chmod 777 run.sh
```

---

## Vídeo executando e mostrando uma análise

---

## Bibliotecas Utilizadas

As bibliotecas utilizadas nessa atividade são as mesmas que as utilizadas na atividade 1, pois os dois projetos são de aprendizado federado.

---

## Metodologia de implementação

Para a implementação do sistema de aprendizado federado, começamos com a criação de um servidor que coordena a troca de informações entre os clientes. Nesse caso, o arquivo do servidor importa as bibliotecas FLwr e as funções necessárias do pacote, definindo uma função que calcula a média ponderada de acurácia dos modelos treinados pelos clientes, criando a estratégia de FedAvg, que define a lógica de treinamento, e define o endereço e porta do servidor. Em seguida, o arquivo inicia o servidor com o número de rodadas definidos de treinamento, e salva um histórico das métricas.

Para implementar o cliente, importamos as bibliotecas necessárias do TensorFlow, e então definimos uma função que constrói o modelo e a classe MyClient, que herda da classe NumPyClient. A classe MyClient define as funções que irão interagir com o servidor: 'get_parameters' para enviar os pesos do modelo para o servidor, 'fit' para receber novos pesos e enviar métricas de treinamento para o servidor, e 'evaluate' para enviar métricas de validação para o servidor.

Por fim, na main do cliente, o código carrega os dados de treinamento e teste aleatoriamente, prepara-os para o formato esperado pelo modelo, instancia o modelo e o cliente, e inicia a comunicação com o servidor através da função 'start_numpy_client'. O servidor coordena as rodadas de treinamento e validação, enviando e recebendo informações dos clientes através dos métodos definidos na classe MyClient, e ao final do treinamento salva as métricas em um arquivo.

---

## Arquivo server.py

Esse arquivo é um servidor para execução de um treinamento de aprendizado federado.

A função weighted_average é definida para realizar a agregação de métricas dos clientes. Essa função recebe um conjunto de métricas (acurácia e número de exemplos) de cada cliente, multiplica a acurácia pelo número de exemplos e, em seguida, calcula a média ponderada dessas acurácias, utilizando o número de exemplos como peso. Isso permite que a avaliação dos clientes com maior número de exemplos tenha mais peso na agregação de métricas.

Em seguida, é criada uma instância da classe FedAvg da biblioteca Flwr, que implementa a estratégia de treinamento federado FedAvg. São definidos alguns parâmetros, como o número mínimo de clientes para treinamento e avaliação e a função de agregação de métricas, que é a weighted_average criada anteriormente.

O servidor é inicializado na porta 8000 e é configurado para executar 40 rodadas de treinamento federado, utilizando a estratégia FedAvg definida anteriormente. O histórico de treinamento é salvo em um arquivo pickle com nome "history_(quantidade de rodadas).pkl".

Ao executar esse servidor, ele ficará aguardando conexões de dispositivos clientes para participar do treinamento. Quando um cliente se conecta, o servidor distribui o modelo atual para o cliente, que realiza o treinamento com seus próprios dados locais e envia de volta o modelo atualizado. O servidor utiliza o modelo enviado pelo cliente para atualizar o modelo global, utilizando a estratégia FedAvg, e o processo é repetido para cada cliente conectado. Ao final das rodadas, o modelo final é retornado para o cliente.

---

## Arquivo client.py

O arquivo de cliente tem uma classe chamada MyClient, que é uma subclasse de flwr.client.NumPyClient. Esta classe define três funções:

* get_parameters(config): retorna os pesos do modelo como um array NumPy.
* fit(parameters, config): atualiza o modelo com os pesos dados pelo servidor, usando um mini-batch do conjunto de treinamento local, e retorna os novos pesos atualizados para o servidor.
* evaluate(parameters, config): avalia o modelo atual com os pesos dados pelo servidor, usando o conjunto de teste local e retorna a perda e acurácia para o servidor.

No código principal, o cliente carrega o conjunto de dados MNIST usando fetch_openml() e divide aleatoriamente em conjuntos de treinamento e teste. O conjunto de dados é então pré-processado e modelado usando a função define_model(). Um objeto MyClient é então criado usando o modelo, os conjuntos de treinamento e teste e o servidor é iniciado chamando flwr.client.start_numpy_client(), que se conecta ao servidor usando o endereço fornecido pelo servidor. O cliente se conecta com o servidor e, a partir daí, o servidor orquestra o treinamento e a avaliação do modelo em um ambiente federado, conforme definido pela estratégia do servidor.

---

## Gráficos

---

## Conclusão
