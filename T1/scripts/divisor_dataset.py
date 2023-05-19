# Importar as bibliotecas necessárias
import tensorflow as tf
import numpy as np
import os

# Baixar os dados MNIST
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# shuffle the training data
p = np.random.permutation(len(x_train))
x_train = x_train[p]
y_train = y_train[p]

# Normalizar os dados
x_train = x_train / 255.0
x_test = x_test / 255.0

y_train = np.eye(10)[y_train] 
y_test = np.eye(10)[y_test]

# Dividir os dados de treino em cinco conjuntos diferentes
x_train_1, x_train_2, x_train_3, x_train_4, x_train_5 = np.split(x_train, 5)
y_train_1, y_train_2, y_train_3, y_train_4, y_train_5 = np.split(y_train, 5)

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
np.save("../treino/x_train_4.npy", x_train_4)
np.save("../treino/y_train_4.npy", y_train_4)
np.save("../treino/x_train_5.npy", x_train_5)
np.save("../treino/y_train_5.npy", y_train_5)

# Salvar os dados de teste em arquivos numpy na pasta de teste
np.save("../teste/x_test.npy", x_test)
np.save("../teste/y_test.npy", y_test)