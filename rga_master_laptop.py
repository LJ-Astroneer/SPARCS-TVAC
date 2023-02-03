# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 17:56:26 2022

@author: Logan Jensen
"""
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm
import time
t0 = time.time()

'''
This block accepts the date input from the user and then turns that into the path to find the data.
The big loop basically turns each file into an array of text lines, it is searching for 3 entries in the header. First is the pirani pressure reading in the header, the position of that heading is then used to know where to pull the pirani pressure and total pressure from. Next, the electon multiplier status becasue if the EM is on then the pressure values will need to be corrected to be comparable to the non EM values (divide by sensitivity increase ~1000). Finally it collects the status of the filalment to determine when the quadrapole is turned on and therefore the total pressure is needed instead of pirani. The relevant data is put into arrays that are then transformed into their appropriate data types.
'''   
head_pirani = []
head_totalp = []
data = []
head_time = []
filament = []
num_file = []
amu=[]
pp=[]
pp_times=[]
j = 0

#date = input('What folder?\n')
date = '5.5.22'
path = r'D:\OneDrive - Arizona State University\LASI-Alpha\Documents\RGA_Data\{}'.format(date)
path = os.path.abspath(path)
folder = os.listdir(path)     
for entry in tqdm(folder, desc='Reading Files',ncols=100):
    with open(path+'\\'+entry, 'r') as file:
        text = file.readlines()
        
        #becasue we do not know the full content of these lines, the .index command used below would not work
        #instead this code filters the file to lines that contain the string, then the line in parsed to pull out the data
        em_text = list(filter(lambda a: "EnableElectronMultiplier" in a, text))
        em_state = int(em_text[0][-3])
        
        pirani_text = list(filter(lambda a: "PiraniPressureOut" in a, text))
        head_pirani.append(pirani_text[0][25:-2])
        
        totalp_text = list(filter(lambda a: "TotalPressureOut" in a, text))
        head_totalp.append(totalp_text[0][24:-2])
        
        filament_text = list(filter(lambda a: "FilamentStatus" in a, text))
        filament.append(filament_text[0][22])
        
        d_start = text.index('</ConfigurationData>\n')+1 #becasue this is always a line in the text right before the data, use this as a marker
        head_time.append(text[d_start][0:23]) #just the time from the first data point
        
        data = text[d_start:]
        data_split = []
        for line in data:
            l = line.split(',')
            data_split.append(l)  
        file_pp_times = [item[0] for item in data_split]
        file_amu = [float(item[1]) for item in data_split]
        if em_state == 1:
            file_pp = [float(item[2])/1000 for item in data_split]
        else:
            file_pp = [float(item[2]) for item in data_split]
        nums = [j]*(len(text)-d_start)
    pp_times.extend(file_pp_times)
    amu.extend(file_amu)
    pp.extend(file_pp)
    num_file.extend(nums)
    j+=1

'''
Convert everything into the right data type and array
'''
head_pirani = np.asarray(head_pirani)
head_pirani = head_pirani.astype(np.float64)
head_totalp = np.asarray(head_totalp)
head_totalp = head_totalp.astype(np.float64)
filament = np.asarray(filament)
pp = np.asarray(pp)
pp  = pp.astype(np.float64)
amu = np.asarray(amu)
amu = amu.astype(np.float64)
'''
This section turns the header time strings and parses them into real date values to do the math that converts the time of a file to the time from the start of the run in both seconds and hours.
'''    
start_head_time = datetime.strptime(head_time[0],'%Y/%m/%d %H:%M:%S.%f')
head_time_from_start = []
time_list = []
for entry in tqdm(head_time,desc='Finding Times',ncols=75):
    time_entry = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_list.append(time_entry)
    time_diff = time_entry - start_head_time
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
pressure = allpressure.copy()
pressure[zeros[0]] = np.nan
times = alltime.copy()
times[zeros[0]] = np.nan
date = alldate.copy()
date[zeros[0]] = np.nan
hour = allhour.copy()
hour[zeros[0]] = np.nan
#gets rid of zeros that are noise and not real data, just lack of data
zeros = np.where(pp == 0.0)
pp[zeros[0]] = np.nan
starts = np.where(amu == min(amu))
amu_seq = amu[starts[0][0]:starts[0][1]]

#%% 
'''
Plots the pressure in the chamber over time, makes a line for the switchover point, and inserts a note about the lowest pressure reached and the total time run.
'''
pressure_plot_q = input('Pressure Plot? [y/n]\n')
if pressure_plot_q == 'y':
    lowest_pressure = np.nanmin(pressure)
    last_time = hour[-1]
    annotation = "Lowest Pressure = {:.2e} Torr\nTotal Time = {:.2f} Hours".format(lowest_pressure,last_time)
    plt.figure()
    plt.semilogy(hour,pressure,label='Pressure Data')
    plt.ylabel('Total Pressure (Log Torr)')
    plt.xlabel('Time From Pump Start (Hr)')
    plt.title('Chamber Pressure vs. Time')
    plt.axvline(x=hour[switch],color='red',linestyle='dotted',label='Pirani to Total pressure switch')
    #plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    #plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.plot([], [], ' ', label=annotation)
    plt.legend(loc='upper right')
    plt.show()

#%%
'''
The Code below plots the data only at full amu values rather than partial values.
Can use this to select a range later

This literally plots the whole sequence of pressure data but for each amu vs time
'''
water_q = input('Water plot? [y/n]\n')
if water_q == 'y':
    seq = np.arange(16,19) #water is 16,17,18; air is 28,32,40
    i=0
    plt.figure()
    for mass in tqdm(seq,desc='plotting',ncols=75):
        i+=1
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start,pres,label=str(mass)+' amu')
    plt.yscale('log')
    plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Pressures for H20 species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    #plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    #plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.legend()
    plt.show()
air_q = input('Air plot? [y/n]\n')
if air_q == 'y':
    seq = np.array([28,32,40]) #water is 16,17,18; air is 28,32,40
    i=0
    plt.figure()
    for mass in tqdm(seq,desc='plotting',ncols=75):
        i+=1
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start,pres,label=str(mass)+' amu')
    plt.yscale('log')
    plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Pressures for Air species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    #plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    #plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.legend()
    plt.show()
nitro_q = input('Nitro plot? [y/n]\n')
if nitro_q == 'y':
    seq = np.array([14,28]) #water is 16,17,18; air is 28,32,40
    i=0
    plt.figure()
    for mass in tqdm(seq,desc='plotting',ncols=75):
        i+=1
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start,pres,label=str(mass)+' amu')
    plt.yscale('log')
    plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Pressures for Nitrogen species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    #plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    #plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.legend()
    plt.show()
#%%
'''
Plotting the newest full RGA Scan
'''
new_q = input('Newest Mass plot? [y/n]\n')
if new_q == 'y':
    seq = amu_seq #water is 16,17,18; air is 28,32,40
    i=0
    scan = []
    plt.figure()
    plt.scatter(file_amu,file_pp,label=None,c="k",s=3)
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
    plt.show()
#%%
'''
So what this whole thing does is take the individual masses for the sel_amu and it overplots them all over time realtive to the required level they need to reach for a clean chamber.
'''
reqs_q = input('Want Req. plots? [y/n]\n')
if reqs_q=='y':
    #plots the selected amu over time relative to the req
    sel_amu = np.arange(80,151) #[83,84,97,98,111,112,127,136,140,142,148]
    plt.figure()
    for mass in tqdm(sel_amu,desc='plotting',ncols=75):
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start[:len(pres)],pres,label=None)
    plt.axhline(y=3e-11,color='red',linestyle='dotted',label='Requirement 3E-11')
    plt.yscale('log')
    plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Gas Pressures > 80 amu vs. Time')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.xlabel('Time From Vacuum Pumping Start (Hr)')
    # plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    # plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.legend()
    plt.show()
     
    
    #same but with the higher amus
    sel_amu = np.arange(151,301)#[150,169,215,228,233,267,281,297,300]
    plt.figure()
    for mass in tqdm(sel_amu,desc='plotting',ncols=75):
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start[:len(pres)],pres,label=None)
    plt.axhline(y=3e-12,color='red',linestyle='dotted',label='Requirement 3E-12')
    plt.yscale('log')
    plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Gas Pressures > 150 amu vs. Time')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.xlabel('Time From Vacuum Pumping Start (Hr)')
    # plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    # plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.legend()
    plt.show()

misc_q = input('Want Misc. plots? [y/n]\n')
if misc_q=='y':
    sel_amu = np.arange(1,80)
    plt.figure()
    for mass in tqdm(sel_amu,desc='plotting',ncols=75):
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start[:len(pres)],pres,label=None)
    plt.yscale('log')
    plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Gas Pressures < 80 amu vs. Time')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.xlabel('Time From Vacuum Pumping Start (Hr)')
    # plt.axvline(x=25.66,color='blue',linestyle='dotted',label='LN2 System Turned on')
    # plt.axvline(x=168.63,color='blue',linestyle='dotted',label='LN2 System Test 2')
    plt.legend()
    plt.show()
#%% Just timing things
t1 = time.time()
total = t1-t0
print('\n Time to run: {:.2f} sec'.format(total))
#%%
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
