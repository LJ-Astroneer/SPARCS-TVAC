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
from tqdm import tqdm

path = os.path.abspath('/Users/logan/Google Drive/Grad_School/RGA_data/10.15_cleantest/ror')
folder = os.listdir(path)

pirani = []
totalp = []
data = []
for entry in tqdm(folder, desc='Reading Files',ncols=75):
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
for row in tqdm(data,desc='Seperating Lines',ncols=100):
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
for entry in tqdm(times,desc='Finding Times',ncols=100):
    time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_diff = time - start_time
    sec_diff = time_diff.total_seconds()
    time_from_start.append(sec_diff)
time_from_start = np.array(time_from_start)
hours_from_start = np.divide(time_from_start,3600)

n2_time = time_from_start[n2_i]
o2_time = time_from_start[o2_i]
pirani_time = time_from_start[pirani_i]
total_time = time_from_start[total_i]

n2 = pp[n2_i]
o2 = pp[o2_i]
pirani = pp[pirani_i]
total = pp[total_i]
total_clip = np.delete(total,np.arange(1170000,len(total)))
total_time_clip = np.delete(total_time,np.arange(1170000,len(total)))

from scipy.signal import savgol_filter
yhat = savgol_filter(total_clip, 2001, 4)

plt.figure()
plt.plot(total_time_clip,total_clip,total_time_clip,yhat)
plt.title("Total Pressure vs Time")
plt.ylabel("Log (Torr)")
plt.xlabel("Seconds")

#%% Lesker Rate of Rise formula analysis
'''
https://www.lesker.com/newweb/faqs/index.cfm?tag=Leaks
Q = rate of rise or Gas Load

Q = ((P2 – P1)*V)/T where the result is in Torr.Liters/Second Where:

Q = Throughput, or Gas Load, or Rate of Rise
P1 = Pressure at the beginning of the test
P2 = Pressure at the end of the test
V = The volume of the chamber, in Liters
T = The time between readings of P1 and P2 , in Seconds

1 – 3 x 10-5 Torr.liters/sec = Good, clean leak free
4 – 6 x 10-5 Torr.liters/sec = Probably dirty, maybe a small leak
7 – 9 x 10-5 Torr.liters/sec = Probably dirty and leaking
1 x 10-4 Torr.liters/sec = Dirty and leaking

 0.76 atmospheric-cc/sec = 1.0 Torr-liters/sec
 1 Torr X 1 Atm/760Torr – 1 liter X 1000cc/1 liter / second or about 0.76 atmospheric-cc/sec = 1.0 Torr-liters/sec
 
 
 https://www.engineeringtoolbox.com/vacuum-evacuation-time-d_844.html
 says we should be able to pump down in seconds not days....
'''
qs = []
gf = []
for i in range(1,50000):
    test_index = i
    P1 = yhat[0]
    P2 = yhat[test_index]
    V = 226 #24^3 = 13824 in^3 ~= 226 L
    T = total_time_clip[test_index]
    Q = ((P2-P1)*V)/T
    gfi = ((P2-P1)*V)
    gf.append(gfi)
    qs.append(Q)
print("Rate of Rise: {} Torr*L/sec".format(np.median(qs)))
convert = np.median(qs)*0.76
print("Rate of Rise: {} STD*cc/sec".format(convert))



















