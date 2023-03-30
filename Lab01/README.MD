# Laboratório de Paralelismo 

## Compilação e Execução

Dentro da pasta Lab01, abra o terminal e execute o seguinte comando
```
python3 paralelismo.py num_threads vetor
```
Onde `num_threads` é o número de threads nas quais serão divididas o vetor, e `vetor` é a sequencia de todos os números do vetor, separados por espaço

Por exemplo:
```
python3 ordenacao.py 4 10 8 7 6 5 4 3 2 1 9
````
Isso irá ordenar o vetor `[10, 8, 7, 6, 5, 4, 3, 2, 1, 9]` usando `quatro` threads.

---

## Bibliotecas Utilizadas

As seguintes bibliotecas são utilizadas no script:

`multiprocessing`: fornece suporte para criação de processos. Usamos sua função `Pipe()` para criar um canal de comunição entre processo pai e filho, para que o processo filho envie o vetor ordenado ao pai. Usamos sua função `Process(target, args)` para criar um processo, enviando como parâmetro a assinatura da função que será paralelizada e os argumentos que a função irá utilizar.

`sys`: fornece acesso a algumas variáveis usadas ou mantidas pelo interpretador e a funções que interagem fortemente com o interpretador. A usamos para receber por parâmetro os valores do número de threads e o vetor.

---

## Funções 

* **`merge`**: 

irá mesclar dois vetores em um único vetor. A função recebe uma conexão com o processo filho e os dois vetores a serem unidos como entrada e compara cada posição dos vetores, organizando-os ordenadamente no vetor resultante e, após isso, envia o vetor para o processo pai pela conexão criada pela `Pipe()` e encerra o processo filho usando a função `.close()`.

Esse procedimento é feito em complexidade `O(n)`, sendo `n` o `número total de elementos em ambos vetores de entrada`, uma vez que nenhuma função de ordenação é chamada pra ordenar o vetor resultante e a função irá percorrer cada elemento dos vetores de entrada exatamente uma vez. Assim, o número de iterações necessárias é diretamente proporcional ao número total de elementos nos vetores de entrada, e o vetor resultante terá também `n` elementos.


* **`bubble_sort`**: 

Irá ordenar um vetor em ordem crescente. A função recebe uma conexão com o processo filho e um vetor como entrada e ordena o vetor usando o algoritmo bubble sort. Em seguida, a função envia o vetor ordenado para o processo pai por meio da cpnexão criada pela `Pipe()` e encerra o processo filho usando a função `.close()`.

---

## Função Principal

A função principal recebe dois argumentos da linha de comando: o número de threads a ser usado e o vetor a ser ordenado. O vetor é dividido em subvetores e cada subvetor é ordenado usando o algoritmo bubble sort em um processo separado. Os subvetores ordenados são então mesclados usando o algoritmo merge até que um único vetor ordenado seja obtido. O vetor final ordenado é impresso no console.

A função principal usa o módulo multiprocessing para criar processos e a classe Pipe para criar um pipe entre os processos pai e filho para comunicação. O método start é usado para iniciar os processos e o método join é usado para aguardar a conclusão dos processos.