import pandas as pd

def load_data():
    data = pd.read_csv("object_detection_data.csv")
    data = data.values.tolist()
    #print(data)
    return data

load_data()