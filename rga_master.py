# -*- coding: utf-8 -*-
"""
Created on Tue May 18 16:07:56 2021

@author: logan

The master code to do all of the things that the RGA data might need to do
"""
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm
from scipy.signal import savgol_filter

path = os.path.abspath('./test')
folder = os.listdir(path)
        
head_pirani = []
head_totalp = []
data = []
head_time = []
em_data = []
em_headers = []
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
        if 'EnableElectronMultiplier="0"' in elem:
            d_start = p_i+5
            data.extend(file[d_start:len(file)])   
        if 'EnableElectronMultiplier="1"' in elem:
            d_start = p_i+5
            em_data.extend(file[d_start:len(file)])
            em_headers.append(entry)
            
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

ht_arr = np.array(head_time)

zeros = np.where(head_totalp == 0.0)
alltotal = np.delete(head_totalp,zeros[0])
alldate = np.delete(ht_arr, zeros[0])
alltime = np.delete(head_time_from_start,zeros[0])
allhours = np.delete(head_hours_from_start,zeros[0])
#%%

times = []
amu = []
pp = []
em_pp = []
x = 0
for row in tqdm(data,desc='Seperating Lines',ncols=75):
    times.append(row[0])
    amu.append(row[1])
    pp.append(row[2])
    x+=1
for row in tqdm(em_data,desc='EM Seperating Lines',ncols=75):
    times.append(row[0])
    amu.append(row[1])
    em_pp.append(row[2])
del(data)
del(em_data)

em_pp = np.asarray(em_pp)
em_pp = em_pp.astype(np.float64)
em_pp = em_pp/1000
    
amu = np.asarray(amu)
amu = amu.astype(np.float64)

pp = np.asarray(pp)
pp  = pp.astype(np.float64)
pp = np.append(pp,em_pp)
zeros = np.where(pp == 0.0)
pp[zeros[0]] = np.nan

starts = np.where(amu == min(amu))
amu_seq = amu[starts[0][0]:starts[0][1]]


#%%
'''
The Code below plots the data only at full amu values rather than partial values.
Can use this to select a range later

This literally plots the whole sequence of pressure data but for each amu vs time
'''
seq = np.arange(1,10)
i=0
plt.figure()
for mass in tqdm(seq,desc='plotting',ncols=75):
    i+=1
    index = np.where(amu == mass)
    pres = pp[index[0]]
    plt.plot(pres,label=str(mass))
plt.yscale('log')
plt.ylabel('Log(Torr)')
plt.xlabel('Time from Start (hours)')
plt.title('Pressure for Select Species (amu) vs. Time')
plt.legend()

#%%
'''
So what this whole thing does is take the individual masses for the sel_amu and it overplots them all over time realtive to the required level they need to reach for a clean chamber.
'''

trim_time = head_hours_from_start

#plots the selected amu over time relative to the req
sel_amu = np.arange(1,150) #[83,84,97,98,111,112,127,136,140,142,148]
plt.figure()
for mass in tqdm(sel_amu,desc='plotting',ncols=75):
    index = np.where(amu == mass)
    pres = pp[index[0]]
    plt.plot(trim_time[:len(pres)],pres,label=None)
line = np.arange(min(trim_time),max(trim_time),10)
req = plt.scatter(line,np.ones(len(line))*3e-11,label='Requirement 3E-11',marker='*')
plt.yscale('log')
plt.title('Partial Gas Pressures > 80 amu vs. Time')
plt.ylabel('Partial Pressure (log Torr)')
plt.xlabel('Time From Vacuum Pumping Start (Hr)')
plt.legend()

#same but with the higher amus
sel_amu = np.arange(150,300)#[150,169,215,228,233,267,281,297,300]
plt.figure()
for mass in tqdm(sel_amu,desc='plotting',ncols=75):
    index = np.where(amu == mass)
    pres = pp[index[0]]
    plt.plot(trim_time[:len(pres)],pres,label=None)
line = np.arange(min(trim_time),max(trim_time),10)
req = plt.scatter(line,np.ones(len(line))*3e-12,label='Requirement 3E-12',marker='*')
plt.yscale('log')
plt.title('Partial Gas Pressures > 150 amu vs. Time')
plt.ylabel('Partial Pressure (log Torr)')
plt.xlabel('Time From Vacuum Pumping Start (Hr)')
plt.legend()


sel_amu = np.arange(1,301)#[150,169,215,228,233,267,281,297,300]
dataframe = np.empty([len(sel_amu),len(trim_time)])
i=0
for mass in tqdm(sel_amu,desc='build array',ncols=100):
    index = np.where(amu == mass)
    pres = pp[index[0]]
    dataframe[i,:len(pres)] = pres
    i+=1

plt.figure()
pressures = dataframe[:,22555]
plt.scatter(np.arange(1,301),pressures,label=None,c="k",s=15)
plt.yscale('log')
line = np.arange(0,301,10)
req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.axvline(x=80,c='c')
plt.axvline(x=150,c='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber at 50C')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

#%% plots the pressure over time
plt.figure()
plt.semilogy(allhours,alltotal)
plt.ylabel('Total Pressure (Log Torr)')
plt.xlabel('Time From Pump Start (Hr)')
plt.title('Chamber Pressure vs. Time')

#%%paper specific plot
plt.figure()
pressures = dataframe[:,18190]
plt.scatter(np.arange(1,301),pressures,label="Before Bakeout",c="k",s=15)
pressures = dataframe[:,21000]
plt.scatter(np.arange(1,301),pressures,label="After Bakeout",marker='x',c='r',s=10)
plt.yscale('log')
plt.legend()
plt.title('RGA scan of TVAC Chamber Before and After 3 day bakeout')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

plt.figure()
pressures = dataframe[:,18190]
plt.plot(np.arange(1,301),pressures,label="Before Bakeout",c="k")
pressures = dataframe[:,21000]
plt.plot(np.arange(1,301),pressures,label="After Bakeout",c='r',linestyle='dashed')
plt.yscale('log')
plt.legend()
plt.title('RGA scan of TVAC Chamber Before and After 3 day bakeout')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

diff = dataframe[:,21000] - dataframe[:,18190]
np.where(diff > 0)
