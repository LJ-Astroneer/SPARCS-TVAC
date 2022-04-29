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
import datetime

path = os.path.abspath('/Users/logan/Google Drive/RGA_data/comparison')
folder = os.listdir(path)
file = []
for entry in folder:
    with open(path+'\\'+entry, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        i = 0
        for line in csv_reader:
            if '</ConfigurationData>' in line:
                data_start = i+1
            file.append(line)
            i+=1
    
data = file[data_start:len(file)]
times = []
amu = []
pp = []
x = 0
for line in data:
    times.append(line[0])
    amu.append(line[1])
    pp.append(line[2])
    x+=1
amu = np.asarray(amu)
amu = amu.astype(np.float64)
pp = np.asarray(pp)
pp  = pp.astype(np.float64)

#%%
'''
Second Step, sort data by sequences
'''
starts = np.where(amu == np.min(amu))[0] #starting point of each sequence
step = starts[1] #number of points in a sequence
n = len(starts) #number of sequences
amu_seq = amu[starts[0]:step] #one sequence of amu steps
seqs = np.empty([n,starts[1]]) #create array for pp data by sequence
for i in range(n):
    nums = pp[starts[i]:starts[i]+step]
    seqs[i,:] = nums

start_seq = []
for start in starts:
    start_seq.append(times[start])

start_times = []
for date in start_seq:
    time = date[11:]
    start_times.append(time)

pressure = []
for i in range(n):
    p = np.sum(seqs[i,:])
    pressure.append(p)
total_pressure = np.array(pressure)

plt.semilogy(total_pressure)
start_time = datetime.strptime(start_seq[0],'%Y/%m/%d %H:%M:%S.%f')
end_time = datetime.strptime(start_seq[-1],'%Y/%m/%d %H:%M:%S.%f')
run_time = end_time - start_time
plt.title("Time Elapsed:    {}".format(run_time))



