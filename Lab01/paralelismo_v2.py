import multiprocessing
import sys
import time

def merge(vector1, vector2, conn):
    """
    Merges two vectors in a single vector
    """
    vector_merged = []
    i = 0
    j = 0
    while i < len(vector1) and j < len(vector2):
        if vector1[i] < vector2[j]:
            vector_merged.append(vector1[i])
            i += 1
        else:
            vector_merged.append(vector2[j])
            j += 1
    while i < len(vector1):
        vector_merged.append(vector1[i])
        i += 1
    while j < len(vector2):
        vector_merged.append(vector2[j])
        j += 1
    conn.send(vector_merged)
    conn.close()

def bubble_sort(vector, conn):
    """
    Sorts a vector using the bubble sort algorithm
    """
    for i in range(len(vector)):
        for j in range(len(vector)-1):
            if vector[j] > vector[j+1]:
                vector[j], vector[j+1] = vector[j+1], vector[j]
    conn.send(vector)
    #print the number of the thread and the number of elements sorted
    print("Thread: ",multiprocessing.current_process().name, "sorted: ", len(vector))
    conn.close()

   

def sort_vector(vector, thread_count):
    vector_separated = [vector[i::thread_count] for i in range(thread_count)]

    processes = []
    for i in range(thread_count):
        parent_conn, child_conn = multiprocessing.Pipe()
        process = multiprocessing.Process(target=bubble_sort, args=(vector_separated[i], child_conn))
        processes.append(process)
        processes[i].vector = parent_conn

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    sorted_vector = [process.vector.recv() for process in processes]

    while len(sorted_vector) > 1:
        vector_of_vectors = []
        while len(sorted_vector) > 1:
            vector1 = sorted_vector.pop(0)
            vector2 = sorted_vector.pop(0)
            vector_of_vectors.append([vector1, vector2])
        if len(sorted_vector) == 1:
            vector_of_vectors.append(sorted_vector[0])


        processes = []
        last_vector = []

        for i in range(len(vector_of_vectors)):
            parent_conn, child_conn = multiprocessing.Pipe()
            if i < len(vector_of_vectors) and type(vector_of_vectors[i][0]) == list:
                process = multiprocessing.Process(target=merge, args=(vector_of_vectors[i][0], vector_of_vectors[i][1], child_conn))
                processes.append(process)
                processes[i].vector = parent_conn
            else:
                last_vector = vector_of_vectors[i]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        sorted_vector = [process.vector.recv() for process in processes]
        if last_vector != []:
            sorted_vector.append(last_vector)


    return sorted_vector[0]
if __name__ == '__main__':
    
    # get vector as args from command line
    vector = [int(x) for x in sys.argv[2:]]

    # get the amount of threads to use from command line
    threads = int(sys.argv[1])

    start_time = time.time()
    sorted_vector = sort_vector(vector, threads)
    end_time = time.time()

    print(f"Sorted vector with {threads} threads: {sorted_vector}")
    print(f"Time taken to sort: {end_time - start_time}")
