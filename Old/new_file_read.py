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

path = os.path.abspath('/Users/logan/Google Drive/RGA_data/comparison')
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

#%%
'''
Second Step, sort data by sequences
'''
starts = np.where(amu == np.min(amu))[0] #starting point of each sequence
step = starts[0] #number of points in a sequence
n = len(starts) #number of sequences
amu_seq = amu[starts[0]:step] #one sequence of amu steps
seqs = np.empty([n,starts[0]]) #create array for pp data by sequence
for i in range(n):
    nums = pp[starts[i]:starts[i]+step]
    for ii in range(len(nums)):
        seqs[i,ii] = nums[ii]

start_seq = []
for start in starts:
    start_seq.append(times[start])

start_times = []
for date in start_seq:
    time = date[11:]
    start_times.append(time)

time_from_start = []
start_time = datetime.strptime(start_seq[0],'%Y/%m/%d %H:%M:%S.%f')
for entry in start_seq:
    time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_diff = time - start_time
    sec_diff = time_diff.total_seconds()
    time_from_start.append(sec_diff)
hours_from_start = np.divide(time_from_start,3600)

totalp = np.array(totalp, dtype=np.float64)
plt.semilogy(hours_from_start,totalp)
end_time = datetime.strptime(start_seq[-1],'%Y/%m/%d %H:%M:%S.%f')
run_time = end_time - start_time
plt.title("Time Elapsed:    {}".format(run_time))
plt.xlabel('Hours from Start')
plt.ylabel('Log Pressure Torr')

avgs = []

for i in range(1,len(totalp)):
    entries = totalp[i-1:i+3]
    avg = np.mean(entries)
    avgs.append(avg)






















