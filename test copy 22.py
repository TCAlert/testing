import pickle 

with open(r"C:\Users\deela\Downloads\processed-master-all.pickle", 'rb') as f:
    data = pickle.load(f)

    print(data)