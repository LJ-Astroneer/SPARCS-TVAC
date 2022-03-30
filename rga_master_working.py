# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 17:56:26 2022

@author: logan
"""
import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm
from scipy.signal import savgol_filter

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
filament = []
em_track = []
num_file = []
j = 0
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
            tracker = [1]*len(file[d_start:len(file)])
            em_track.extend(tracker)
            nums = [j]*len(file[d_start:len(file)])
            num_file.extend(nums)
        if 'EnableElectronMultiplier="1"' in elem:
            d_start = p_i+5
            data.extend(file[d_start:len(file)])
            tracker = [1000]*len(file[d_start:len(file)])
            em_track.extend(tracker)
            nums = [j]*len(file[d_start:len(file)])
            num_file.extend(nums)
    for i, elem in enumerate(str_file):
        if 'FilamentStatus' in elem:
           p_i = i
    filament.append(str_file[p_i][24])
    j+=1

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
time_list = []
for entry in tqdm(head_time,desc='Finding Times',ncols=75):
    time = datetime.strptime(entry,'%Y/%m/%d %H:%M:%S.%f')
    time_list.append(time)
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
#%% hails from total_pressure_mk2
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

#%%
'''
Breaks the data files down into their components of time, atomic mass unit (amu), and partial pressure (pp). Then deletes data and em_data to save memory. Divides the em data by 1000 to account for the sensitivity increase and combines with the other data. 

NOTE: I tried to write a sorting code for the times so that if the EM got turned on and off throughout testing the data would still get put into the right order. Unfortunately the way I have done this is by using the time attached to each measurement, which means you have to parse every single time stamp, which is slow and may be too slow. Only other way I can think is to give all the partial pressures a time based on the file heading instead so there is less parsing but I do now know how I would make that work
    -did it, see bottom loop made a tracker for the file number the data came from (num_file) then used that to create the time arrays
    - also means that there is no shufflin/unshuffling to do becasue I also created a file tro track if the em was on (em_track) that putsa 1 for off or 1000 for on. Then just divide pp by that and boom autoadjusted
'''
amu = []
pp = []
x = 0
for row in tqdm(data,desc='Seperating Partial Pressures',ncols=75):
    amu.append(row[1])
    pp.append(row[2])
    x+=1
pp = np.asarray(pp)
pp  = pp.astype(np.float64)
em_track = np.asarray(em_track)
em_track = em_track.astype(np.float64)
pp = pp/em_track
amu = np.asarray(amu)
amu = amu.astype(np.float64)

#gets rid of zeros that are noise and not real data, just lack of data
zeros = np.where(pp == 0.0)
pp[zeros[0]] = np.nan
starts = np.where(amu == min(amu))
amu_seq = amu[starts[0][0]:starts[0][1]]

#give values a time using the header for the file it came from
num_file = np.asarray(num_file)
pp_times = np.empty(np.shape(amu),dtype=datetime)
pp_time_from_start = np.empty(np.shape(amu))
pp_hours_from_start = np.empty(np.shape(amu))
for i in range(j):
    pp_times[num_file==i] = time_list[i]
    pp_time_from_start[num_file==i] = head_time_from_start[i]
    pp_hours_from_start[num_file==i] = head_hours_from_start[i]

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
        plt.plot(head_hours_from_start,pres,label=str(mass))
    plt.yscale('log')
    plt.title('Partial Pressures for H20 species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
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
        plt.plot(head_hours_from_start,pres,label=str(mass))
    plt.yscale('log')
    plt.title('Partial Pressures for Air species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()
#%%
'''
So what this whole thing does is take the individual masses for the sel_amu and it overplots them all over time realtive to the required level they need to reach for a clean chamber.
'''
reqs_q = input('Want Req. plots? [y/n]\n')
if reqs_q=='y':
    #plots the selected amu over time relative to the req
    sel_amu = np.arange(1,81) #[83,84,97,98,111,112,127,136,140,142,148]
    plt.figure()
    for mass in tqdm(sel_amu,desc='plotting',ncols=75):
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start[:len(pres)],pres,label=None)
    plt.axhline(y=3e-11,color='red',linestyle='dotted',label='Requirement 3E-11')
    plt.yscale('log')
    plt.title('Partial Gas Pressures > 80 amu vs. Time')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.xlabel('Time From Vacuum Pumping Start (Hr)')
    plt.legend()
    plt.show()
     
    
    #same but with the higher amus
    sel_amu = np.arange(80,300)#[150,169,215,228,233,267,281,297,300]
    plt.figure()
    for mass in tqdm(sel_amu,desc='plotting',ncols=75):
        index = np.where(amu == mass)
        pres = pp[index[0]]
        plt.plot(head_hours_from_start[:len(pres)],pres,label=None)
    plt.axhline(y=3e-12,color='red',linestyle='dotted',label='Requirement 3E-12')
    plt.yscale('log')
    plt.title('Partial Gas Pressures > 150 amu vs. Time')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.xlabel('Time From Vacuum Pumping Start (Hr)')
    plt.legend()
    plt.show()

#%%
# sel_amu = np.arange(1,301)#[150,169,215,228,233,267,281,297,300]
# dataframe = np.empty([len(sel_amu),len(head_hours_from_start)])
# i=0
# for mass in tqdm(sel_amu,desc='build array',ncols=100):
#     index = np.where(amu == mass)
#     pres = pp[index[0]]
#     dataframe[i,:len(pres)] = pres
#     i+=1

# plt.figure()
# pressures = dataframe[:,22555]
# plt.scatter(np.arange(1,301),pressures,label=None,c="k",s=15)
# plt.yscale('log')
# line = np.arange(0,301,10)
# req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
# req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
# plt.axvline(x=80,c='c')
# plt.axvline(x=150,c='m')
# plt.legend()
# plt.title('RGA Scan of Vacuum Chamber at 50C')
# plt.xlabel('Gas Species (amu)')
# plt.ylabel('Partial Pressure (log Torr)')

# #%%paper specific plot
# plt.figure()
# pressures = dataframe[:,18190]
# plt.scatter(np.arange(1,301),pressures,label="Before Bakeout",c="k",s=15)
# pressures = dataframe[:,21000]
# plt.scatter(np.arange(1,301),pressures,label="After Bakeout",marker='x',c='r',s=10)
# plt.yscale('log')
# plt.legend()
# plt.title('RGA scan of TVAC Chamber Before and After 3 day bakeout')
# plt.xlabel('Gas Species (amu)')
# plt.ylabel('Partial Pressure (log Torr)')

# plt.figure()
# pressures = dataframe[:,18190]
# plt.plot(np.arange(1,301),pressures,label="Before Bakeout",c="k")
# pressures = dataframe[:,21000]
# plt.plot(np.arange(1,301),pressures,label="After Bakeout",c='r',linestyle='dashed')
# plt.yscale('log')
# plt.legend()
# plt.title('RGA scan of TVAC Chamber Before and After 3 day bakeout')
# plt.xlabel('Gas Species (amu)')
# plt.ylabel('Partial Pressure (log Torr)')

# diff = dataframe[:,21000] - dataframe[:,18190]
# np.where(diff > 0)
