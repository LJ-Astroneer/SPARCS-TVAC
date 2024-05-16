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

wv = file[:,0]
med = np.median(data_array,axis=1)
std = np.std(data_array,axis=1)
mad = stats.median_abs_deviation(data_array,axis=1)
snr = med/mad

plt.ion()
f = plt.figure()
f.set_figheight(7)
f.set_figwidth(10)
graph1 = f.add_subplot(221)
graph2 = f.add_subplot(222)
graph3 = f.add_subplot(223)
graph4 = f.add_subplot(224)

x, y = wv,med
y2=std
reads = data_array
def graph(x,y,y2,reads):
    graph1.clear()
    graph2.clear()
    graph3.clear()
    graph4.clear()
    graph1.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
    graph1.set_title('Median w/ Std.dev Error')
    graph2.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
    graph2.set_title('Median w/ Std.dev Error (log)')
    graph2.set_yscale('log')
    graph3.plot(reads)
    graph3.set_title('Raw data')
    graph4.plot(reads)
    graph4.set_title('Raw data (log)')
    graph4.set_yscale('log')
    f.canvas.draw()
    f.canvas.flush_events()
graph(x,y,y2,reads)