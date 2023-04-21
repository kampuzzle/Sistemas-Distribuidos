#!/bin/bash

# Run the client 5 times in parallel
for i in {1..5}; do
    python3 cliente.py &
done

# Run the server in the background
python3 server.py &

# Wait for all processes to finish
wait
