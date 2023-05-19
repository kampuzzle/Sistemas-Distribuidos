import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# read all the csvs from the clients_history_1 folder
dir_hist = "clients_history_1"

csvs = []
for file in os.listdir(dir_hist):
    if file.endswith(".csv"):
        df = pd.DataFrame(columns=['round_id', 'accuracy'], data=np.genfromtxt(dir_hist+ "/" +file, delimiter=','))
        csvs.append(df)


# plot the accuracy of each client in each round, put a point in each round, x must be equally spaced, interval of 1. put an x where there was no training 
for i in range(len(csvs)):
    plt.plot(csvs[i]['round_id'], csvs[i]['accuracy'], label="client "+str(i+1), marker='o')
    plt.xticks(np.arange(0, max(csvs[i]['round_id']), 1))
    
    for tick in range(int(max(csvs[i]['round_id']))): 
        # if the round was not trained, put an x
        try:
            csvs[i].loc[csvs[i]['round_id'] == tick, 'accuracy'].item()
        except:
            plt.scatter(tick, 0, marker='x', color='red')

    plt.xlabel("round")
    plt.ylabel("accuracy")
    plt.legend()
    plt.title("Accuracy of each client in each round")
    # save the plot in a png file
    plt.savefig("{}/client_".format(dir_hist)+str(i+1)+"_"+dir_hist+".png")
    plt.clf()


# plot a unique graph with all the clients
for i in range(len(csvs)):
    plt.plot(csvs[i]['round_id'], csvs[i]['accuracy'], label="client "+str(i+1), marker='o')
    plt.xticks(np.arange(0, max(csvs[i]['round_id']), 1))
    plt.ylim(0.9, 1)
    
    for tick in range(int(max(csvs[i]['round_id']))): 
        # if the round was not trained, put an x
        try:
            csvs[i].loc[csvs[i]['round_id'] == tick, 'accuracy'].item()
        except:
            plt.scatter(tick, 0, marker='x', color='red')

plt.xlabel("round")
plt.ylabel("accuracy")
plt.legend()
plt.title("Accuracy of each client in each round")
# save the plot in a png file
plt.savefig("{}/all_clients_".format(dir_hist)+dir_hist+".png")
plt.clf()


global_data = pd.read_csv("round_data.csv")

# plot the accuracy of the global model in each round
plt.plot(global_data['round_id'], global_data['global_model_acc'], marker='o')
plt.xticks(np.arange(0, max(global_data['round_id']), 1))
plt.xlabel("round")
plt.ylabel("accuracy")
plt.title("Accuracy of the global model in each round")
# print at the last round the accuracy of the global model near the last point 2 float precision
plt.text(max(global_data['round_id'])-1, global_data['global_model_acc'].iloc[-1] , round(global_data['global_model_acc'].iloc[-1], 2))
# save the plot in a png file
plt.savefig("{}/global_model_".format(dir_hist)+dir_hist+".png")