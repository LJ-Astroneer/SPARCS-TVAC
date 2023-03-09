# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 17:56:26 2022

@author: Logan Jensen
"""
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.markers import MarkerStyle
import csv
import os
from datetime import datetime
from tqdm import tqdm
import time
import sys
from temp_read import read_temps
t0 = time.time()

'''
This block accepts the date input from the user and then turns that into the path to find the data.
The big loop basically turns each file into an array of text lines, it is searching for 3 entries in 
the header. First is the pirani pressure reading in the header, the position of that heading is then 
used to know where to pull the pirani pressure and total pressure from. Next, the electon multiplier 
status becasue if the EM is on then the pressure values will need to be corrected to be comparable 
to the non EM values (divide by sensitivity increase ~1000). Finally it collects the status of the 
filalment to determine when the quadrapole is turned on and therefore the total pressure is needed 
instead of pirani. The relevant data is put into arrays that are then transformed into their 
appropriate data types.
'''   
head_pirani = []
head_totalp = []
data = []
head_time = []
filament = []
# num_file = []
amu=[]
pp=[]
pp_times=[]
em = []
j = 0

date = input('What RGA folder?\n')

#date = '5.5.22'
path = r'C:/Users/sesel/OneDrive - Arizona State University/LASI-Alpha/Documents/RGA_Data/{}'.format(date)
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
        
        filament_text = list(filter(lambda a: "FilamentStatus" in a, text))[0][22]
        filament.append(filament_text)
        
        d_start = text.index('</ConfigurationData>\n')+1 #becasue this is always a line in the text right before the data, use this as a marker
        head_time.append(text[d_start][0:23]) #just the time from the first data point

        data = text[d_start:]
        data_split = []
        for line in data:
            l = line.split(',')
            data_split.append(l)  
        file_amu = [float(item[1]) for item in data_split]
        if (filament_text=='6' or filament_text=='3'): #3 and 6 both mean filament is on an running normally
            if em_state == 1:
                file_pp = [float(item[2])/1000 for item in data_split]
            else:
                file_pp = [float(item[2]) for item in data_split]
        else:
            file_pp = [np.nan for item in data_split]
            file_amu = [np.nan for item in data_split]
        
    amu.extend([file_amu])
    pp.extend([file_pp])
    em.append([em_state])
    j+=1

'''
Convert everything into the right data type and array
'''
head_pirani = np.asarray(head_pirani)
head_pirani = head_pirani.astype(np.float64)
head_pirani[np.where(head_pirani==0.0001)]=np.nan #removes any line with 1E-4 becasue that means the pirani gauge is bottomed out
head_totalp = np.asarray(head_totalp)
head_totalp = head_totalp.astype(np.float64)
filament = np.asarray(filament)
pp = np.asarray(pp)
pp  = pp.astype(np.float64)
amu = np.asarray(amu)
amu = amu.astype(np.float64)

'''
This section turns the header time strings and parses them into real date values 
to do the math that converts the time of a file to the time from the start of 
the run in both seconds and hours.
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
Colects all the data together including the pirani and total pressure data 
using the filament status as the switching point. 

'''    
pirani=np.where((filament!='6')&(filament!='3')) #pirani pressure only useful when filament is off (removed 1E-4's already)
total=np.where((filament=='6')|(filament=='3')) #total p only useful when filament is on
allpressure = np.zeros(j)
allpressure[pirani] = head_pirani[pirani]
allpressure[total] = head_totalp[total]

times = head_time_from_start
hour = head_hours_from_start
date = np.array(head_time)

'''
These lines remove the 0.000 startup error files from the RGA where the outputs
from the header like pressure are not filled in yet.

0's are also removed from the partial pressure list becasue these values mean
that the EM is not on and the RGA is effectively measuring noting at that amu.
HOWEVER, haveing a 0 in the dataset can be misleading then since we want low
numbers. So it is better to remove the data so it does not show on plots.
'''
zeros = np.where(allpressure == 0.0)
pressure = allpressure.copy()
pressure[zeros] = np.nan
pp[np.where(pp==0)]=np.nan #removes the 0's from non EM low partial pressures
amu_fil_on = amu[np.where((filament=='6')|(filament=='3'))] #only the amus where the filament is on
pp_fil_on = pp[np.where((filament=='6')|(filament=='3'))] #only the amus where the filament is on
amu_seq = amu_fil_on[0] #full amu sequenc
amu_seq_int = amu_seq[amu_seq == amu_seq.astype(int)] #only the whole number amus

amu_int = amu[:,[amu_seq == amu_seq.astype(int)][0]] #pulls all the integer amus from amu array
pp_int = pp[:,[amu_seq == amu_seq.astype(int)][0]] #pulls all pp from integer amus in pp array

amu_int_fil_on = amu_fil_on[:,[amu_seq == amu_seq.astype(int)][0]] #pulls all the integer amus from amu array
pp_int_fil_on = pp_fil_on[:,[amu_seq == amu_seq.astype(int)][0]] #pulls all pp from integer amus in pp array
pressure_fil_on = pressure[np.where((filament=='6')|(filament=='3'))]

#%% 

'''
Plots the pressure in the chamber over time, makes a line for the switchover 
point, and inserts a note about the lowest pressure reached and the total time run.
'''
pressure_plot_q = input('Pressure Plot? [y/n]\n')
if pressure_plot_q == 'y':
    lowest_pressure = np.nanmin(pressure)
    last_time = hour[-1]
    annotation = "Lowest Pressure = {:.2e} Torr\nTotal Time = {:.2f} Hours".format(lowest_pressure,last_time)
    plt.figure()
    plt.scatter(hour,pressure,label='Pressure Data')
    plt.yscale('log')
    plt.ylabel('Total Pressure (Log Torr)')
    plt.xlabel('Time From Pump Start (Hr)')
    plt.title('Chamber Pressure vs. Time')
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
#water ions cover a wider range than 16,17,18 but those are common markers for it
if water_q == 'y':
    plt.figure()
    mass1 = np.where(amu==16)
    mass2 = np.where(amu==17)
    mass3 = np.where(amu==18)    
    pres1 = pp[mass1]    
    pres2 = pp[mass2] 
    pres3 = pp[mass3]
    plt.scatter(hour[mass1[0]],pres1,label='16 amu')
    plt.scatter(hour[mass2[0]],pres2,label='17 amu')
    plt.scatter(hour[mass3[0]],pres3,label='18 amu')
    plt.yscale('log')
    #plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Pressures for H20 species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()

air_q = input('Air plot? [y/n]\n')
#air typically shows up at 14,28 for N and N2; 16,32 for O and O2; also 40 for Argon
#skipped 16 since it more stronly tracks water
if air_q == 'y':
    plt.figure()
    mass1 = np.where(amu==14)
    mass2 = np.where(amu==28)
    mass3 = np.where(amu==32)    
    mass4 = np.where(amu==40)
    pres1 = pp[mass1]    
    pres2 = pp[mass2] 
    pres3 = pp[mass3]
    pres4 = pp[mass4]
    plt.scatter(hour[mass1[0]],pres1,label='14 amu, N')
    plt.scatter(hour[mass2[0]],pres2,label='28 amu, N2')
    plt.scatter(hour[mass3[0]],pres3,label='32 amu, O2')
    plt.scatter(hour[mass4[0]],pres4,label='40 amu, Ar')
    plt.yscale('log')
    #plt.ylim(bottom=5e-14) #5e-14 is the minimum detectable partial pressure with EM on
    plt.title('Partial Pressures for Air species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()

nitro_q = input('Nitro plot? [y/n]\n')
#just nitrogen ions, 14 for N and N2++; 28 for N2
if nitro_q == 'y':
    mass1 = np.where(amu==14)
    mass2 = np.where(amu==28)
    pres1 = pp[mass1]    
    pres2 = pp[mass2]   
    plt.figure()
    plt.scatter(hour[mass1[0]],pres1,label='14 amu, N')
    plt.scatter(hour[mass2[0]],pres2,label='28 amu, N2')
    plt.yscale('log')
    plt.title('Partial Pressures for Nitrogen species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()

def custom_trackplot():
    masses = input ('What AMU? Comma seperated, no spaces\n')
    masses = masses.split(',')
    masses = np.asarray(masses)
    masses = masses.astype(np.float64)
    plt.figure()
    for mass in masses:
        i = np.where(amu==mass)
        y = pp[i]
        x = hour[i[0]]
        plt.scatter(x,y,label=(str(mass)+' amu'))
    plt.yscale('log')
    plt.title('Partial Pressures for Nitrogen species over time')
    plt.xlabel('Time from Start (Hr)')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()
#%%
'''
Plotting the newest full RGA Scan with requirement lines
'''
new_q = input('Newest Mass plot? [y/n]\n')
if new_q == 'y':
    plt.figure()
    #plt.scatter(amu[-1],pp[-1],s=3,c='k')
    plt.plot(amu[-1],pp[-1],c='k')    
    plt.yscale('log')
    plt.title('Most recent RGA scan')
    plt.xlabel('AMU')
    plt.ylabel('Partial Pressure (log Torr)')
    line = np.arange(0,301,10)
    req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
    req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
    annotation = "Total Pressure = {:.2e} Torr\nTotal Time = {:.2f} Hours".format(pressure[-1],hour[-1])
    plt.plot([], [], ' ', label=annotation)
    plt.legend()
    plt.axvline(x=80,c='c')
    plt.axvline(x=150,c='m')
    plt.show()

def custom_fullplot():
    print('Below is the list of valid file timestamps')
    np.set_printoptions(threshold=sys.maxsize)
    print(ht_arr[np.where(np.isnan(pressure) == False)])
    np.set_printoptions(threshold = False)
    first_t=input('Input first timestamp (copy paste from above)\n')
    # second_t=input('Input second timestamp (copy paste from above)\n')
    first = np.where(ht_arr==first_t)[0][0]
    # second = np.where(ht_arr==second_t)[0][0]
    # tbtw = int(hour[second]-hour[first])
    plt.figure()
    plt.plot(amu[first],pp[first],label='{num}'.format(num=first_t),c='k')
    line = np.arange(0,301,10)
    plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
    plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
    plt.axvline(x=80,c='c')
    plt.axvline(x=150,c='m')
    annotation = "Total Pressure = {:.2e} Torr\nTotal Time = {:.2f} Hours".format(pressure[first],hour[first])
    plt.plot([], [], ' ', label=annotation)
    plt.yscale('log')
    plt.title('30C RGA scan')
    plt.xlabel('AMU')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()
    
#%%
comp_q = input('Compare Scans? [y/n]\n')
if comp_q=='y':
    print('Below is the list of valid file timestamps')
    np.set_printoptions(threshold=sys.maxsize)
    print(ht_arr[np.where(np.isnan(pressure) == False)])
    np.set_printoptions(threshold = False)
    first_t=input('Input first timestamp (copy paste from above)\n')
    second_t=input('Input second timestamp (copy paste from above)\n')
    first = np.where(ht_arr==first_t)[0][0]
    second = np.where(ht_arr==second_t)[0][0]
    tbtw = int(hour[second]-hour[first])
    plt.figure()
    m=MarkerStyle('o','none')
    plt.scatter(amu[first],pp[first],label='{num}'.format(num=first_t),c='r',marker=m)
    plt.scatter(amu[second],pp[second],label='{num}'.format(num=second_t),c='k')
    line = np.arange(0,301,10)
    req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
    req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
    plt.axvline(x=80,c='c')
    plt.axvline(x=150,c='m')
    annotation = "Time Between Scans {t} Hours".format(t=tbtw)
    plt.plot([], [], ' ', label=annotation)
    plt.yscale('log')
    plt.title('Most recent RGA scan')
    plt.xlabel('AMU')
    plt.ylabel('Partial Pressure (log Torr)')
    plt.legend()
    plt.show()

#%% Check RGA is working well
'''
This is inspired by the RGA failure we had, this will not be an input call but 
a function that you can run at any time and look at them youself
'''
def health_check():
    x = np.nansum(pp_int_fil_on,axis=1)
    y = pressure_fil_on.copy()
    mag_diff = np.log10(x)-np.log10(y)
    plt.figure()
    plt.plot(mag_diff)
    plt.title('Magnitude difference between sum of partial pressures and total pressure')
    plt.ylabel('Magnitude difference log10(sum)-log10(total)')
    print(mag_diff)
#%% Temps
'''
Import temp data
'''
temp_q = input('Want to work with temperature data? [y/n]\n')
if temp_q == 'y':
    temp_file = input('Enter directory for temp file, ensure to delete the ""\n')
    ttimes, tzone1, tzone2, tzone3, tzone4, tzone5, tzone6 = read_temps(temp_file)
    
    '''
    Parsing the temperature times
    '''
    ttime_list=[]
    ttime_from_start = []
    for entry in ttimes:
        ttime_entry = datetime.strptime(entry,'%Y-%m-%d %H:%M:%S')
        ttime_list.append(ttime_entry)
        ttime_diff = ttime_entry - start_head_time
        tsec_diff = ttime_diff.total_seconds()
        ttime_from_start.append(tsec_diff)
    ttime = np.array(ttime_from_start)
    thours = np.divide(ttime_from_start,3600)
    
    '''
    Pressure plot with temp data
    '''
    pressure_plot_q = input('Pressure Plot? [y/n]\n')
    if pressure_plot_q == 'y':
        lowest_pressure = np.nanmin(pressure)
        last_time = hour[-1]
        fig,ax1 = plt.subplots()
        ax2=ax1.twinx()
        l2 = ax2.scatter(thours,tzone1,label='Temperature Zone 1',c='r',s=1)
        l1 = ax1.scatter(hour,pressure,label='Pressure Data',c='b')
        ax1.set_yscale('log')
        ax1.set_ylabel('Total Pressure (Log Torr)',color='b')
        ax2.set_ylabel('Temperature (°C)',color='r')
        ax1.set_xlabel('Time From Pump Start (Hr)')
        plt.title('Chamber Pressure vs. Time')
        annotation = "Lowest Pressure = {:.2e} Torr\nTotal Time = {:.2f} Hours".format(lowest_pressure,last_time)
        plt.annotate(annotation,xy=(43,80),xytext=(50,80))
        plt.legend([l2,l1],['Temp Zone 1','Pressure Data'])
        plt.show()