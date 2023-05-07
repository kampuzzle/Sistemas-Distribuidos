# Importar as bibliotecas necessárias
import tensorflow as tf
import numpy as np
import os

# Baixar os dados MNIST
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# Dividir os dados de treino em três conjuntos diferentes
x_train_1, x_train_2, x_train_3 = np.split(x_train, 3)
y_train_1, y_train_2, y_train_3 = np.split(y_train, 3)

# Criar as pastas de treino e teste se não existirem
os.makedirs("../treino", exist_ok=True)
os.makedirs("../teste", exist_ok=True)

# Salvar os dados de treino em arquivos numpy na pasta de treino
np.save("../treino/x_train_1.npy", x_train_1)
np.save("../treino/y_train_1.npy", y_train_1)
np.save("../treino/x_train_2.npy", x_train_2)
np.save("../treino/y_train_2.npy", y_train_2)
np.save("../treino/x_train_3.npy", x_train_3)
np.save("../treino/y_train_3.npy", y_train_3)

# Salvar os dados de teste em arquivos numpy na pasta de teste
np.save("../teste/x_test.npy", x_test)
np.save("../teste/y_test.npy", y_test)