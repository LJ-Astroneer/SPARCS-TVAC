# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 13:59:03 2020

@author: logan
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
for row in tqdm(data,desc='Seperating Lines',ncols=100):
    times.append(row[0])
    amu.append(row[1])
    pp.append(row[2])
    x+=1
for row in tqdm(em_data,desc='EM Seperating Lines',ncols=100):
    times.append(row[0])
    amu.append(row[1])
    em_pp.append(row[2])

em_pp = np.asarray(em_pp)
em_pp = em_pp.astype(np.float64)
em_pp = em_pp/1000
    
amu = np.asarray(amu)
amu = amu.astype(np.float64)

pp = np.asarray(pp)
pp  = pp.astype(np.float64)
pp = np.append(pp,em_pp)

starts = np.where(amu == min(amu))
amu_seq = amu[starts[0][0]:starts[0][1]]

# dataframe = np.empty([len(amu_seq),len(head_time_from_start)])
# i=0
# for mass in tqdm(amu_seq,desc='build array',ncols=100):
#     index = np.where(amu == mass)
#     pres = pp[index[0]]
#     dataframe[i,:] = pres
#     i+=1

# s = np.sum(dataframe[:,0])
# norm = np.divide(dataframe[:,0],s)
# n_arr = np.empty(np.shape(dataframe))
# for i in range(len(head_time_from_start)):
#     n_arr[:,i] = norm

# norm_pres = np.divide(dataframe,n_arr)

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
    plt.plot(head_hours_from_start,pres,label=str(mass))
plt.yscale('log')



#%%
'''
trim the bake outs out of the pressure data

used to make a pretty figure by manually removing the bakeout peaks and plateus to show decrease in pressure over time
'''
trim_total = np.empty([0,0])
trim_total = np.append(trim_total,alltotal[0:1544])
trim_total = np.append(trim_total,alltotal[3414:3598])
trim_total = np.append(trim_total,alltotal[4820:6240])
trim_total = np.append(trim_total,alltotal[7500:12910])
trim_total = np.append(trim_total,alltotal[15531])
trim_total = np.append(trim_total,alltotal[16892])
trim_total = np.append(trim_total,alltotal[18200])

trim_time = np.empty([0,0])
trim_time = np.append(trim_time,alltime[0:1544])
trim_time = np.append(trim_time,alltime[3414:3598])
trim_time = np.append(trim_time,alltime[4820:6240])
trim_time = np.append(trim_time,alltime[7500:12910])
trim_time = np.append(trim_time,alltime[15531])
trim_time = np.append(trim_time,alltime[16892])
trim_time = np.append(trim_time,alltime[18200])


plt.figure()
plt.semilogy(trim_time,trim_total)
#%%
'''
So what this whole thing does is take the individual masses for the sel_amu and it overplots them all over time realtive to the required level they need to reach for a clean chamber.
'''
#btw you should use a mask in the future but oh well
i1 = np.arange(500,1544)
i1b = np.arange(3414,3598)
i2 = np.arange(4820,6240)
i3 = np.arange(7500,12910)
i4 = np.arange(15530,15531)
i5 = np.arange(16891,16892) 
i6 = np.arange(18200,18201)
i7 = np.arange(20009)
 
trim_index = np.array([i1])
trim_index = np.append(trim_index,i1b)
trim_index = np.append(trim_index,i2)
trim_index = np.append(trim_index,i3)
trim_index = np.append(trim_index,i4)
trim_index = np.append(trim_index,i5)
trim_index = np.append(trim_index,i6)
trim_index = np.append(trim_index,i7)

#I think what it was meant to do was speed up the plotting by removing all but 200 randomly chosen data points from the data set, but then I still add in the last 3 data points so that the randomness still includes the most recent data.
random = sorted(np.random.randint(0,len(trim_index),size=200))
random = np.append(random,[len(trim_index)-3,len(trim_index)-2,len(trim_index)-1])
trim_index = trim_index[random]
trim_time = head_hours_from_start[trim_index]

 


sel_amu = [83,84,97,98,111,112,127,136,140,142,148]
plt.figure()
for mass in tqdm(sel_amu,desc='plotting',ncols=75):
    index = np.where(amu == mass)
    pres = pp[index[0][trim_index]]
    #pres = savgol_filter(pres,11,3)
    plt.plot(trim_time,pres,label=None)
line = np.arange(min(trim_time),max(trim_time),10)
req = plt.scatter(line,np.ones(len(line))*3e-11,label='Requirement 3E-11',marker='*')
plt.yscale('log')
plt.title('Partial Gas Pressures > 80 amu vs. Time')
plt.ylabel('Partial Pressure (log Torr)')
plt.xlabel('Time From Vacuum Pumping Start (Hr)')
plt.legend()


sel_amu = np.arange(150,300)#[150,169,215,228,233,267,281,297,300]
trim_time = head_hours_from_start[trim_index]
plt.figure()
for mass in tqdm(sel_amu,desc='plotting',ncols=75):
    index = np.where(amu == mass)
    pres = pp[index[0][trim_index]]
    # pres = savgol_filter(pres,21,3)
    plt.plot(trim_time,pres,label=None)
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
    pres = pp[index[0][trim_index]]
    dataframe[i,:] = pres
    i+=1
plt.figure()
pressures = dataframe[:,-1]
zeros = np.where(pressures == 0.0)
pressures[zeros[0]] = np.nan
plt.scatter(np.arange(1,301),pressures,label=None,c="k",s=1)
plt.yscale('log')
line = np.arange(0,301,10)
req = plt.plot(line,np.ones(len(line))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
req = plt.plot(line,np.ones(len(line))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.axvline(x=80,c='c')
plt.axvline(x=150,c='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')



plt.figure()
pressures = dataframe[:,-1]
zeros = np.where(pressures == 0.0)
pressures[zeros[0]] = np.nan
plt.scatter(np.arange(1,301),pressures,label=None,c="k",s=1)
plt.yscale('log')
line = np.arange(0,301,10)
req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.stem([80],[3e-11],linefmt='c',markerfmt='c')
plt.stem([150],[3e-12],linefmt='m',markerfmt='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

plt.figure()
pressures = dataframe[:,-1]
zeros = np.where(pressures == 0.0)
pressures[zeros[0]] = np.nan

plt.scatter(np.arange(1,301),pressures,label=None,c="k",s=3)
plt.yscale('log')
line = np.arange(0,301,10)
req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.axvline(x=80,c='c')
plt.axvline(x=150,c='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')






