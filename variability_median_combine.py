# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 15:16:46 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats
from scipy.optimize import curve_fit

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\variability\fuv_throughput.csv")
nuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\variability\nuv_throughput.csv")
i=0
test=pd.DataFrame(columns=fuv.columns[1:])
while i < len(fuv):
    if i == 81:
        index = np.arange(i,i+1)
        i+=1
    else:
        index = np.arange(i,i+3)
        i+=3
    print(index)
    row=[]
    for label in fuv.columns[1:]:
        value = np.median(fuv.iloc[index][label].values)
        row.append(value)
    test=pd.concat([pd.DataFrame([row], columns=test.columns), test], ignore_index=True)
test.to_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\variability\fuv_throughput_medians.csv")
plt.scatter(test['X(FITS)_T1'].values,test['Y(FITS)_T1'].values,label='FUV')

    
i=0
test=pd.DataFrame(columns=nuv.columns[1:])
while i < len(nuv):
    if i == 63:
        index = np.arange(i,i+6)
        i+=6
    else:
        index = np.arange(i,i+3)
        i+=3
    print(index)
    row=[]
    for label in nuv.columns[1:]:
        value = np.median(nuv.iloc[index][label].values)
        row.append(value)
    test=pd.concat([pd.DataFrame([row], columns=test.columns), test], ignore_index=True)
test.to_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\variability\nuv_throughput_medians.csv")
plt.scatter(test['X(FITS)_T1'].values,test['Y(FITS)_T1'].values,label='NUV')
plt.xlim((0,1175))
plt.ylim((0,1033))
plt.legend()



