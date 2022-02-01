# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:36:07 2020

@author: logan

A file entirely made to compare the files that are in the "comparison" folder.
Files were ordered originally as below:
    1_before.csv (the rga scan from before we did anything to the chamber)
    2_after_beforeheat.csv (the scan after we cleaned the chamber but before heating)
    3_latest.csv (Was the last scan from the chamber)
    4_em.csv (an early scan with the EM on)
    5_lem.csv (latest scan with the EM on)
    6_50c.csv (a scan with the chamber at 50C for req comparison)
"""

import numpy as np
import matplotlib.pyplot as plt 
import csv
import os
from datetime import datetime
from tqdm import tqdm

#universal pathing definition to make sure it always works
path = os.path.abspath('./comparison')
folder = os.listdir(path)

#the below block is what populates the data array with all of the data from the csv files. This does not break the data apart into anything it basically just makes a long as hell array of lines. The enumerate line with the '</ConfigurationData>' is searching for the beginning of the actual data in each file. Everything before that line is the header of the file which is not used in this code.
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

#Now we go about breaking the many rows of the data array into its components. Each row has a time it was collected, the amu the measurement was at, and then the partial pressure. At the end, amu and pp are converted to floats so they are easier to work with.            
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

#so the way that all of the files are read in, they are not seperated by file. This block is what seperates the continuous array into its component files. All of the files in this case were made by using the single scan function in the RGA software so they are all composed of only one mass sweep. That is why the minimum point of the amu list is the definer of the different files.
starts = np.where(amu == min(amu))
amu_seq = amu[starts[0][0]:starts[0][1]]
pp_before = pp[starts[0][0]:starts[0][1]]
pp_after = pp[starts[0][1]:starts[0][2]]
pp_latest = pp[starts[0][2]:starts[0][3]]
#all of the em data needs to be divided by 1000 becasue that is the gain of the EM 
pp_em = pp[starts[0][3]:starts[0][4]]
pp_em = pp_em/1000
pp_lem = pp[starts[0][4]:starts[0][5]]
pp_lem = pp_lem/1000
pp_50 = pp[starts[0][5]:len(pp)]
pp_50 = pp_50/1000

#This plot compares scans in the chamber before John and I wiped it all out and installed the heaters on the shrouds. This is intended to show both the increase in cleanliness from wiping and potential contributions from the adhesives for the heaters. This is something that will be repeated for future equipment installations.
plt.figure()
plt.title("Heater Install Comparison")
plt.semilogy(amu_seq,pp_before,label="Before Install")
plt.semilogy(amu_seq,pp_after,label="After Install")
plt.legend()

#Exactly what is sounds like, comparison before and after all of the baking efforts for the chamber as of 12/2020
plt.figure()
plt.title("Bakout Comparison")
plt.semilogy(amu_seq,pp_em,label="Before Baking")
plt.semilogy(amu_seq,pp_lem,label="After Baking")
plt.legend()

#Just comparing the difference in sensitivity of the RGA with the EM off and On
plt.figure()
plt.title("EM Comparison")
plt.semilogy(amu_seq,pp_latest,label="Before EM")
plt.semilogy(amu_seq,pp_em,label="After EM")
plt.legend()

#This calculates and then shows in log scale the change in partial pressures across the heater install
diff = np.log10(np.divide(pp_after,pp_before))
plt.figure()
plt.plot(amu_seq,diff)
plt.plot(amu_seq,np.zeros(len(amu_seq)))
plt.title("Log Change in pp from Heater Install (log(After/Before))")
plt.ylabel("Log Difference in pp")

#This calculates and then shows in log scale the change in partial pressures across the baking as of 12/2020
diff = np.log10(np.divide(pp_latest,pp_after))
plt.figure()
plt.plot(amu_seq,diff)
plt.plot(amu_seq,np.zeros(len(amu_seq)))
plt.title("Log Difference in pp from Baking (log(After/Before))")
plt.ylabel("Log Difference in pp")


#%% What I was trying to do here was to scale the partial pressure difference data by the abundance of each amu in the initial scan. Since a lot of the partial pressures are really small, a change from 1E-13 to 1E-15 torr would look the same as a change from 1E2 to 1E0 torr (-2) on the log difference plot, however the 1E-13 change is basically negligable while the 1E2 is much more significant. So scaling by the initial abundance emphasizes this significance and highlights changes in the main components of the intial chamber intereior (mainly water and hydrogen components)

from sklearn import preprocessing
norm = preprocessing.normalize(pp_latest.reshape(1,-1))
diff = np.log10(np.divide(pp_latest,pp_after))
diff_abundance = np.multiply(diff,norm)
plt.figure()
plt.plot(amu_seq,diff_abundance[0])
plt.plot(amu_seq,np.zeros(len(amu_seq)))
plt.title("Log Difference in pp from Baking Scaled by Abundance")
plt.ylabel("Log Difference in pp")

#%% Here we are selecting speficic amus, mainly all of the whole numbers. This makes for a cleaner looking scatter plot even if it is not fully accurate. Remember that the "peaks" the RGA is measureing have some thickness (FWHM) similar to a psf. Has something to do with noise terms, temperature changes, and other factors. By doing this we are just plotting the peak point of each psf.

sel_amu = np.arange(1,301)#[150,169,215,228,233,267,281,297,300]
dataframe = np.empty([len(sel_amu),1])
i=0
for mass in tqdm(sel_amu,desc='build array',ncols=100):
    index = np.where(amu_seq == mass)
    pres = pp_50[index[0]]
    dataframe[i,:] = pres
    i+=1

pressures = dataframe[:,-1]
plt.figure()
plt.yscale('log')
plt.ylim(1e-15,1e-6)
plt.scatter(np.arange(1,301),pressures,label=None,c="k",s=5)
#next three lines are how I add the colored lines to the plots that show the requirements for chamber cleanliness as states in the SPARCS CCD. These requirements are actually for when we know bakeout of a specific component is complete but the same thing applies for an empty chamber.
line = np.arange(0,301,10)
req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.axvline(x=80,c='c')
plt.axvline(x=150,c='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber at 50C')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

#%%This section does the same as the one above but it shows a comparison from two seperate scans, in this case to emphaisize how bakeouts have brought the chamber closer to meeting the requirements.

sel_amu = np.arange(1,301)#[150,169,215,228,233,267,281,297,300]
dataframe = np.empty([len(sel_amu),1])
i=0
for mass in tqdm(sel_amu,desc='build array',ncols=100):
    index = np.where(amu_seq == mass)
    pres = pp_em[index[0]]
    dataframe[i,:] = pres
    i+=1

plt.figure()
pressures = dataframe[:,-1]
# plt.plot(np.arange(1,301),pressures,label='Before Bake',c="k")
plt.scatter(np.arange(1,301),pressures,label='Before Bake, total pressure 4.8e-6 Torr',c="#EE442F",s=5,marker='^')

dataframe = np.empty([len(sel_amu),1])
i=0
for mass in tqdm(sel_amu,desc='build array',ncols=100):
    index = np.where(amu_seq == mass)
    pres = pp_lem[index[0]]
    dataframe[i,:] = pres
    i+=1

pressures = dataframe[:,-1]
# plt.plot(np.arange(1,301),pressures,label='After Bake',c="#EE442F")
plt.scatter(np.arange(1,301),pressures,label='After Bake, total pressure 3.5e-8 Torr',c="k",s=5,marker='o')

plt.yscale('log')
plt.ylim(1e-15,1e-6)
line = np.arange(0,301,10)
req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='#63ACBE')
req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.axvline(x=80,c='#63ACBE')
plt.axvline(x=150,c='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber Before and After Chamber Bakeouts')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

