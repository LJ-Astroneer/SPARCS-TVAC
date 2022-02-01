  # -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:36:07 2020

@author: logan
"""
'''
This Code is designed to take all the files from a pupdown of the chamber
mass sweep mode, and collect all of the pirani
and total ion pressure readings. The code also calculates the times
for all of the measurements and returns a "time from start" for consistent plotting.

Total Pressures should be compiled in allpressure
Time from start is compiled in alltime
Time and Date info for all total pressures are in alldate

So for example if you see a spike in the alltime, allpressure plot you can find
the index where that spike is and search for the clock time and date in alldate

i = np.where(alltime >= spike time from start)
spike_time = alldate[min(i)]

Code also automatically estimates the time when to switch over to the total pressure readings from the pirani readings
'''
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm

path = os.path.abspath('./11.20')
folder = os.listdir(path)
        
#the below block is what populates the data array with all of the data from the csv files. This does not break the data apart into anything it basically just makes a long as hell array of lines. The code is searching for two things, first is the pressure readings both pirani and ion total then it is also looking to see what mode the file is in. If the file is in trand mode then the header is in a different format so the starting index for data needed to be changed. Additionally, if your trend settings are collecting data on the pressures, this code grabs that data and collects it as well.
head_pirani = []
head_totalp = []
data = []
head_time = []
for entry in tqdm(folder, desc='Reading Files',ncols=75):
    file = []
    str_file = []
    with open(path+'\\'+entry, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            file.append(line)
            str_file.append(str(line))
    for i, elem in enumerate(str_file):
        if 'PiraniPressureOut' in elem:
            p_i = i
    head_pirani.append(str_file[p_i][27:-3])
    head_totalp.append(str_file[p_i+1][26:-3])
    head_time.append(str_file[p_i+5][2:25])
    for i, elem in enumerate(str_file):
        if 'Mode="Trend"' in elem:
            d_start = p_i+5
            data.extend(file[d_start:len(file)])
            
#%%This section all has to do with the data that is pulled from the headers, including the pressures and the time/data data.            
head_pirani = np.asarray(head_pirani)
head_pirani = head_pirani.astype(np.float64)
head_totalp = np.asarray(head_totalp)
head_totalp = head_totalp.astype(np.float64)    
start_head_time = datetime.strptime(head_time[0],'%Y/%m/%d %H:%M:%S.%f')
head_time_from_start = []
for entry in tqdm(head_time,desc='Finding Times',ncols=75):
    time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_diff = time - start_head_time
    sec_diff = time_diff.total_seconds()
    head_time_from_start.append(sec_diff)
head_time_from_start = np.array(head_time_from_start)
head_hours_from_start = np.divide(head_time_from_start,3600)

#%%reworked this to actually take the right data and put it together
switch = np.where(head_totalp > 1E-4)[0][0]
allpressure = np.append(head_pirani[:switch], head_totalp[switch:])
alltime = head_time_from_start
allhour = head_hours_from_start
alldate = np.array(head_time)

#did this becasue 0.0s would show up in the data for unknown reasons or becasue there were gaps in time? Either way these would cause large spikes in the data that did not really mean anything and made the plot look terrible. This removes those indexes. Also these lines remove the 0.000 startup error files from the RGA, when you first start recording the header output numbers are all 0 and useless for the first file.
zeros = np.where(allpressure == 0.0)
#pressure = np.delete(allpressure,zeros[0])
pressure = allpressure.copy()
pressure[zeros[0]] = np.nan
#time = np.delete(alltime, zeros[0])
time = alltime.copy()
time[zeros[0]] = np.nan
# date = np.delete(alldate, zeros[0])
date = alldate.copy()
date[zeros[0]] = np.nan
#hour = np.delete(allhour, zeros[0])
hour = allhour.copy()
hour[zeros[0]] = np.nan

plt.figure()
plt.semilogy(hour,pressure)
plt.ylabel('Total Pressure (Log Torr)')
plt.xlabel('Time From Pump Start (Hr)')
plt.title('Chamber Pressure vs. Time')

# from scipy.signal import savgol_filter
# yhat = savgol_filter(total_clip, 2001, 4)

# plt.figure()
# plt.plot(total_time_clip,total_clip,total_time_clip,yhat)
# plt.title("Total Pressure vs Time")
# plt.ylabel("Log (Torr)")
# plt.xlabel("Seconds")
















