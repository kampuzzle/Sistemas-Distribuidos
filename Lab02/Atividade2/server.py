import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server import start_server



def weighted_average(metrics):
    # Multiply accuracy of each client by number of examples used
    acc = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]
    

    # Aggregate and return custom metric (weighted average)
    results = {"accuracy": sum(acc) / sum(examples)}
    return results


import pickle 

if __name__ == "__main__":
    # Define strategy
   # Create FedAvg strategy
    strategy = fl.server.strategy.FedAvg(
         min_fit_clients=5,  
        min_evaluate_clients=5, 
        evaluate_metrics_aggregation_fn=weighted_average,
    )

    server_address = "[::]:8000"
    
    num_round = 2
    # Start Flower server for num_round rounds of federated learning
    history = start_server(server_address=server_address,config=fl.server.ServerConfig(num_rounds=num_round), strategy=strategy)
    # Save history
    with open(f"history_{num_round}.pickle", "wb") as f:
        pickle.dump(history, f, protocol=pickle.HIGHEST_PROTOCOL)
