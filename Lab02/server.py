import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server.server import start_server

if __name__ == "__main__":
    # Define strategy
    strategy = FedAvg()

    # Define server config
    server_config = fl.server.ServerConfig(
        grpc_max_message_length=1024 * 1024 * 1024,
        num_rounds=10,
        num_clients=5,
        sample_fraction=0.1,
        min_sample_size=5,
        min_num_clients=2
    )

    # Start Flower server
    start_server(config=server_config, strategy=strategy)
