## Instruções para execução do código 

Primeiro, é necessário criar os dados de treino e teste executando o script dentro de scritps/divisor_dataset.py

Agora, execute o server.py. Em outros terminais, execute os clientes no formato: "python3 cliente.py X", onde X é o numero do cliente, que sera usado para escolher o dataset

Por padrão, o server precisa que no mínimo 3 clientes estejam conectados para começar a treinar o modelo. Para alterar esse valor, basta alterar a variável MIN_CLIENTS dentro de server.py. O server irá escolher aleatoriamente os clientes que irão participar do treinamento, sendo que o número de clientes escolhidos é igual a NUM_CLIENTS.

O server irá treinar o modelo usando os clientes escolhidos e irá enviar o modelo para os clientes. Os clientes irão calcular a acurácia do modelo usando os dados de teste e irão enviar essa acurácia para o server. O server irá calcular a média das acurácias e irá enviar o modelo para os clientes novamente. Esse processo se repete até que o modelo tenha uma acurácia maior que TARGET_ACCURACY ou até que o número máximo de iterações (MAX_ROUNDS) seja atingido.


Ao final da execução, o server irá salvar o modelo treinado em um arquivo .h5 e gerar um arquivo .csv com os dados de cada rodada.


Para visualizar os resultados, execute o script plot_graficos.py. Esse script irá gerar os gráficos de acurácia e perda do modelo ao longo das rodadas e irá salvar esses gráficos em arquivos .png. Para especificar qual historico, mude o nome da variavel do diretorio no codigo para o nome da pasta com os csvs dos historicos desejados.

O script ira gerar um grafico de acuracia e para cada cliente, um comparando todos os clientes, e um com a acurácia para o modelo global. 

