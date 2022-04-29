# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:36:07 2020

@author: logan
"""
'''
'''
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm

path = os.path.abspath('./comparison')
folder = os.listdir(path)
        
data = []
for entry in tqdm(folder, desc='Reading Files',ncols=75):
    file = []
    str_file = []
    with open(path+'\\'+entry, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            file.append(line)
            str_file.append(str(line))
    for i, elem in enumerate(str_file):
        if '</ConfigurationData>' in elem:
            p_i = i
    d_start = p_i+1
    data.extend(file[d_start:len(file)])
            
times = []
amu = []
pp = []
x = 0
for row in tqdm(data,desc='Seperating Lines',ncols=100):
    times.append(row[0])
    amu.append(row[1])
    pp.append(row[2])
    x+=1
amu = np.asarray(amu)
amu = amu.astype(np.float64)
pp = np.asarray(pp)
pp  = pp.astype(np.float64)

starts = np.where(amu == min(amu))
amu_seq = amu[starts[0][0]:starts[0][1]]
pp_seq1 = pp[starts[0][0]:starts[0][1]]
pp_seq2 = pp[starts[0][1]:len(pp)]

# pirani_i = np.where(amu == 5)
# total_i = np.where(amu == 999)

# start_time = datetime.strptime(times[0],'%Y/%m/%d %H:%M:%S.%f')
# time_from_start = []
# for entry in tqdm(times,desc='Finding Times',ncols=100):
#     time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
#     time_diff = time - start_time
#     sec_diff = time_diff.total_seconds()
#     time_from_start.append(sec_diff)
# time_from_start = np.array(time_from_start)
# hours_from_start = np.divide(time_from_start,3600)

# pirani_time = time_from_start[pirani_i]
# total_time = time_from_start[total_i]

# pirani = pp[pirani_i]
# total = pp[total_i]

# alltotal = np.append(total, head_totalp)
# alltime = np.append(total_time, head_time_from_start)

# zeros = np.where(alltotal == 0.0)
# alltotal = np.delete(alltotal,zeros[0])
# alltime = np.delete(alltime, zeros[0])
# #these two lines remove the 0.000 startup error files from the RGA, when you
# #first start recording the header output numbers are all 0 and useless for the
# # first file.


# plt.semilogy(alltime,alltotal)

# # from scipy.signal import savgol_filter
# # yhat = savgol_filter(total_clip, 2001, 4)

# # plt.figure()
# # plt.plot(total_time_clip,total_clip,total_time_clip,yhat)
# # plt.title("Total Pressure vs Time")
# # plt.ylabel("Log (Torr)")
# # plt.xlabel("Seconds")
















