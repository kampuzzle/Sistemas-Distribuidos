import pandas as pd
from matplotlib import pyplot as plt
import os 


if __name__ == "__main__":

    for file in os.listdir("graficos_clients"):
        if file.endswith(".csv"):
            df = pd.read_csv("graficos_clients/" + file)
            #remove first line of dataframe
            df = df.iloc[1:]
            # plot the dataframe, x will be round number, (integer tick), and y will be accuracy
            plt.plot(df["0"], marker='o')            
            plt.title("Acuracia do cliente {}".format(file.split("_")[1][:-4]))
            plt.xlabel("Rounds")
            plt.ylabel("Acuracia")
            plt.savefig("graficos_clients/acuracia_{}.png".format(file.split("_")[1][:-4]))
            plt.clf()