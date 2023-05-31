# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:56:19 2023

@author: sesel
"""

import csv
import numpy as np
import os
import matplotlib.pyplot as plt

filename = 'C:/Users/sesel/OneDrive - Arizona State University/LASI-Alpha/Documents/pico_data/Raw/dich3_5nm_auto_dark.csv'
path = os.path.expanduser(filename)
with open(path,'r', encoding='utf-8-sig', newline='') as csvfile:
    data = list(csv.reader(csvfile))

data=np.asarray(data)
wv = data[:,0].astype(np.float64)
wv_err = 2.5
r = data[:,1]
reads = []
for row in r:
    row = row.replace('[','')
    row = row.replace(']','')
    row = row.split(', ')
    row = [float(i) for i in row]
    reads.append(row)
reads = np.asarray(reads)

avg = np.mean(reads,axis=1)
std = np.std(reads,axis=1)/np.sqrt(len(reads[0]))
plt.figure()
plt.scatter(wv,avg)
plt.errorbar(wv,avg,xerr=wv_err,yerr=std,fmt='o')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Average Current (Amp)')
plt.title('Current versus wavelength with error')
