#!/bin/bash

# Define a list of numbers
# numbers=(2 5 10 20 40)
numbers=(2)

# Loop through each number
for num in "${numbers[@]}"; do
    # Run the server with the current num as argument in the background
   
    # Run the client 5 times in parallel, passing num as argument
    for i in {1..5}; do
        python3 cliente.py "$num" &
    done

    sleep 5

    python3 server.py "$num" &
    sleep 5

    # Wait for all processes to finish
    wait
done
