import random
import time
import sys
from multiprocessing import cpu_count
import csv

from paralelismo import sort_vector


def generate_random_vector(size):
    """
    Generates a random vector of the given size
    """
    return [random.randint(0, 10000) for _ in range(size)]


if __name__ == '__main__':
    vector_sizes = [14, 100, 1000, 10000, 10000]
    process_counts = [1, 2, 4, 6, 8,10,12,14,16]

   
    with open('data/results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["size", "process_num", "time"])

        for size in vector_sizes:
            print(f"Sorting vector of size {size} with {process_counts} process")
           
            for process_count in process_counts:
                print(f"Sorting vector of size {size} with {process_count} process")
                if(size == 100000 and process_count <6): 
                    continue
                    
                vector = generate_random_vector(size)

                start_time = time.time()
                sorted_vector = sort_vector(vector, process_count)
                end_time = time.time()

               
                writer.writerow([size, process_count, end_time - start_time])

                sys.stdout.flush()  