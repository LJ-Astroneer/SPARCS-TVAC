import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
from scipy import stats
def graph(x,y,y2,reads,filename):
    plt.ion()
    f = plt.figure()
    f.set_figheight(7)
    f.set_figwidth(10)
    graph1 = f.add_subplot(221)
    graph2 = f.add_subplot(222)
    graph3 = f.add_subplot(223)
    graph4 = f.add_subplot(224)
    graph1.clear()
    graph2.clear()
    graph3.clear()
    graph4.clear()
    graph1.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
    graph1.set_title('Median w/ Std Error')
    graph1.set_xlabel('Wavelength')
    graph1.set_ylabel('Detected Current (Amp)')
    graph2.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
    graph2.set_title('Median w/ Std Error (log)')
    graph2.set_yscale('log')
    graph2.set_xlabel('Wavelength')
    graph2.set_ylabel('Detected Current (Amp)')
    graph3.plot(x,reads)
    graph3.set_title('Raw data')
    graph3.set_xlabel('Wavelength')
    graph3.set_ylabel('Detected Current (Amp)')
    graph4.plot(x,reads)
    graph4.set_title('Raw data (log)')
    graph4.set_yscale('log')
    graph4.set_xlabel('Wavelength')
    graph4.set_ylabel('Detected Current (Amp)')
    f.suptitle(filename)
    f.canvas.draw()
    f.canvas.flush_events()
    
filenames = ['051424-3x3.csv','051524-2x2.csv','051524-1x1.csv','051524-0.5x0.5.csv']#['051524_allnight.csv']
f2 = plt.figure()
snr_fig = f2.add_subplot(111)
alldata=[]
for filename in filenames:
    file = pd.read_csv("D:/OneDrive - Arizona State University/LASI-Alpha/Documents/pico_data/Raw/"+filename)
    file = file.to_numpy()
    data_array = []
    for i in range(len(file)):
        data = ast.literal_eval(file[i,1])
        data_array.append(data)
    
    wv = file[:,0]
    med = np.median(data_array,axis=1)
    std = np.std(data_array,axis=1)/np.sqrt(50) #stadnard errror
    mad = stats.median_abs_deviation(data_array,axis=1)
    snr = med/std
    
    snr_fig.plot(wv,snr)

    x, y = wv,med
    y2=std
    reads = data_array
    alldata.append(y)
    graph(x,y,y2,reads,filename)

snr_fig.set_title('Median / Standard Error')
snr_fig.set_xlabel('Wavelength')
snr_fig.legend(['12nm bandpass','8nm bandpass','4nm bandpass','2nm bandpass'])


#%% Make a plot of all the scans to compare normalized so you can overplot them
plt.figure()    
plt.plot(x,alldata[0]/np.median(alldata[0]),'-x')
plt.plot(x,alldata[1]/np.median(alldata[1]),'-x')
plt.plot(x,alldata[2]/np.median(alldata[2]),'-x')
plt.plot(x,alldata[3]/np.median(alldata[3]),'-x')
plt.yscale('log')
plt.legend(['12nm bandpass','8nm bandpass','4nm bandpass','2nm bandpass'])
plt.title('Photodiode readings, mean normaized')
plt.ylabel('Normalized Current (log)')
plt.xlabel('Wavelength (nm)')    
#%% Make a plot of the ratios of all the scans to each other, normalized sop they can be overplotted
plt.figure()    
plt.plot(x,(alldata[0]/(alldata[1]))/np.median((alldata[0]/(alldata[1]))),'-x',label='12nm / 8nm')
plt.plot(x,(alldata[0]/(alldata[2]))/np.median((alldata[0]/(alldata[2]))),'-x',label='12nm / 4nm')
plt.plot(x,(alldata[0]/(alldata[3]))/np.median((alldata[0]/(alldata[3]))),'-x',label='12nm / 2nm')
plt.plot(x,(alldata[1]/(alldata[2]))/np.median((alldata[1]/(alldata[2]))),'-x',label='8nm / 4nm')
plt.plot(x,(alldata[1]/(alldata[3]))/np.median((alldata[1]/(alldata[3]))),'-x',label='8nm / 2nm')
plt.plot(x,(alldata[2]/(alldata[3]))/np.median((alldata[2]/(alldata[3]))),'-x',label='4nm / 2nm')
plt.legend()