import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
from scipy import stats

file = pd.read_csv('C:/Users/sesel/OneDrive - Arizona State University/LASI-Alpha/Documents/pico_data/Raw/051424-0.5x0.5.csv')
file = file.to_numpy()
data_array = []
for i in range(len(file)):
    data = ast.literal_eval(file[i,1])
    data_array.append(data)

med = np.median(data_array,axis=1)
std = np.std(data_array,axis=1)
mad = stats.median_abs_deviation(data_array,axis=1)
snr = med/mad

