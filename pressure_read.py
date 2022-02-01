# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 15:45:05 2020

@author: logan
"""
'''
First step, load in packages and the data
'''
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime

path = os.path.abspath('./11.20')
folder = os.listdir(path)

pirani = []
totalp = []
data = []
for entry in folder:
    file = []
    with open(path+'\\'+entry, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            file.append(line)
    pirani.append(str(file[294])[27:-3])
    totalp.append(str(file[295])[26:-3])
    data.extend(file[299:len(file)])
    
times = []
amu = []
pp = []
x = 0
for row in data:
    times.append(row[0])
    amu.append(row[1])
    pp.append(row[2])
    x+=1
amu = np.asarray(amu)
amu = amu.astype(np.float64)
pp = np.asarray(pp)
pp  = pp.astype(np.float64)


#%% Sort the values
n2_i = np.where(amu == 28)
o2_i = np.where(amu == 32)
pirani_i = np.where(amu == 5)
total_i = np.where(amu == 999)

start_time = datetime.strptime(times[0],'%Y/%m/%d %H:%M:%S.%f')
time_from_start = []
for entry in times:
    time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_diff = time - start_time
    sec_diff = time_diff.total_seconds()
    time_from_start.append(sec_diff)
time_from_start = np.array(time_from_start)
hours_from_start = np.divide(time_from_start,3600)

n2_time = time_from_start[n2_i]
o2_time = time_from_start[o2_i]
pirani_time = time_from_start[pirani_i]
total_time = hours_from_start[total_i]

n2 = pp[n2_i]
o2 = pp[o2_i]
pirani = pp[pirani_i]
total = pp[total_i]






















