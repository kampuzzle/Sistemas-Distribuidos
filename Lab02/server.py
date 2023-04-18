import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server import start_server

from cliente import MyClient


def weighted_average(metrics):
    # Multiply accuracy of each client by number of examples used
    acc = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    results = {"accuracy": sum(acc) / sum(examples)}
    return results

if __name__ == "__main__":
    # Define strategy
   # Create FedAvg strategy
    strategy = fl.server.strategy.FedAvg(
  
        min_evaluate_clients=5,  
       
        evaluate_metrics_aggregation_fn=weighted_average,
    )


    server_address = "[::]:8080"
    # Start Flower server
    server = start_server(server_address=server_address,config=fl.server.ServerConfig(num_rounds=1), strategy=strategy)

    #print("Server started at", server_address)

    #print metrics of each round
    for i in range(1):
        print(server.get_metrics())

    # save model
    model = server.get_model()
    model.save("model.h5")
