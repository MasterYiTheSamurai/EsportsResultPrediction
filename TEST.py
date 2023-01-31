import pandas as pd

def function():
    df = pd.read_csv("matches.csv", nrows=100)
    ser = df.dtypes
    print(ser)
    dict = ser.to_dict()

    dftmp = pd.read_csv("matches.csv", low_memory=False)
    #Youngjun Song

    print("Success")


function()