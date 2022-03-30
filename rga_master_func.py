Fi# -*- coding: utf-8 -*-
"""
Created on Tue May 18 16:07:56 2021

@author: logan

The master code to do all of the things that the RGA data might need to do
Codes in Master Currently: total_pressure_mk2
"""
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm
from scipy.signal import savgol_filter

#%%
'''
This block accepts the date input from the user and then turns that into the path to find the data.
The big loop basically turns each file into an array of text lines, it is searching for 3 entries in the header. First is the pirani pressure reading in the header, the position of that heading is then used to know where to pull the pirani pressure and total pressure from. Next, the electon multiplier status becasue if the EM is on then the pressure values will need to be corrected to be comparable to the non EM values (divide by sensitivity increase ~1000). Finally it collects the status of the filalment to determine when the quadrapole is turned on and therefore the total pressure is needed instead of pirani. The relevant data is put into arrays that are then transformed into their appropriate data types.
'''
date = input('What folder?\n')
path = '/Users/logan/Documents/Real_Documents/Grad_School/Research/SPARCS/RGA_data/{}'.format(date)
path = os.path.abspath(path)
folder = os.listdir(path)        
head_pirani = []
head_totalp = []
data = []
head_time = []
em_data = []
em_headers = []
filament = []

for entry in tqdm(folder, desc='Reading Files',ncols=75):
    file = []
    str_file = []
    with open(path+'\\'+entry, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            file.append(line)
            str_file.append(str(line))
    for i, elem in enumerate(str_file):
        p_i = i
        if 'PiraniPressureOut' in elem:
            head_pirani.append(str_file[p_i][27:-3])
            head_totalp.append(str_file[p_i+1][26:-3])
            head_time.append(str_file[p_i+5][2:25])
        if 'EnableElectronMultiplier="0"' in elem:
            d_start = p_i+5
            data.extend(file[d_start:len(file)])   
        if 'EnableElectronMultiplier="1"' in elem:
            d_start = p_i+5
            em_data.extend(file[d_start:len(file)])
            em_headers.append(entry)
        if 'FilamentStatus' in elem: 
            filament.append(str_file[p_i][24])
head_pirani = np.asarray(head_pirani)
head_pirani = head_pirani.astype(np.float64)
head_totalp = np.asarray(head_totalp)
head_totalp = head_totalp.astype(np.float64)
filament = np.asarray(filament)
'''
This section turns the header time strings and parses them into real date values to do the math that converts the time of a file to the time from the start of the run in both seconds and hours.
'''    
start_head_time = datetime.strptime(head_time[0],'%Y/%m/%d %H:%M:%S.%f')
head_time_from_start = []
for entry in tqdm(head_time,desc='Finding Times',ncols=75):
    time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_diff = time - start_head_time
    sec_diff = time_diff.total_seconds()
    head_time_from_start.append(sec_diff)
head_time_from_start = np.array(head_time_from_start)
head_hours_from_start = np.divide(head_time_from_start,3600)
ht_arr = np.array(head_time)
'''
Colects all the data together including the pirani and total pressure data using the filament status as the switching point. 
'''
switch = np.where(filament=='3')[0][1] #1 index after switch to get updated pressure
allpressure = np.append(head_pirani[:switch], head_totalp[switch:])
alltime = head_time_from_start
allhour = head_hours_from_start
alldate = np.array(head_time)
'''
Did this becasue 0.0s would show up in the data for unknown reasons or becasue there were gaps in time? Either way these would cause large spikes in the data that did not really mean anything and made the plot look terrible. This removes those indexes. Also these lines remove the 0.000 startup error files from the RGA, when you first start recording the header output numbers are all 0 and useless for the first file.
'''
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
#%%
'''
Plots the pressure in the chamber over time, makes a line for the switchover point, and inserts a note about the lowest pressure reached and the total time run.
'''
pressure_plot_q = input('Pressure Plot? [y/n]\n')
if pressure_plot_q == 'y':
    lowest_pressure = np.nanmin(pressure)
    last_time = hour[-1]
    annotation = "Lowest Pressure = {:.2e} Torr\nFinal Time = {:.2f} Hours".format(lowest_pressure,last_time)
    plt.figure()
    plt.semilogy(hour,pressure,label='Pressure Data')
    plt.ylabel('Total Pressure (Log Torr)')
    plt.xlabel('Time From Pump Start (Hr)')
    plt.title('Chamber Pressure vs. Time')
    plt.axvline(x=hour[switch],color='red',linestyle='dotted',label='Pirani to Total pressure switch')
    plt.legend()
    plt.figtext(0.5,0.7,annotation)
    plt.show()

