# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 15:45:05 2020

@author: logan
"""

import numpy as np
import matplotlib.pyplot as plt
import csv
import os

path = os.path.abspath('/Users/logan/Desktop/RGA_data/9.28.20/MassSpecData-06553-20200928-150007.csv')
file = []
with open(path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    
    for line in csv_reader:
        file.append(line)
        
data = []
for i in range(137,137+2999):
    data.append(file[i])

amu = []
for i in range(len(data)):
    amu.append(float(data[i][1]))
   
    
pp = []
for i in range(len(data)):
    pp.append(float(data[i][2]))
    
plt.plot(amu,pp)














