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
pp_before = pp[starts[0][0]:starts[0][1]]
pp_after = pp[starts[0][1]:starts[0][2]]
pp_latest = pp[starts[0][2]:starts[0][3]]
pp_em = pp[starts[0][3]:starts[0][4]]
pp_em = pp_em/1000
pp_lem = pp[starts[0][4]:starts[0][5]]
pp_lem = pp_lem/1000
pp_50 = pp[starts[0][5]:len(pp)]
pp_50 = pp_50/1000

plt.figure()
plt.title("Heater Install Comparison")
plt.semilogy(amu_seq,pp_before,label="Before Install")
plt.semilogy(amu_seq,pp_after,label="After Install")
plt.legend()

plt.figure()
plt.title("Bakout Comparison")
plt.semilogy(amu_seq,pp_em,label="Before Baking")
plt.semilogy(amu_seq,pp_lem,label="After Baking")
plt.legend()

plt.figure()
plt.title("EM Comparison")
plt.semilogy(amu_seq,pp_latest,label="Before EM")
plt.semilogy(amu_seq,pp_em,label="After EM")
plt.legend()

diff = np.log10(np.divide(pp_after,pp_before))
plt.figure()
plt.plot(amu_seq,diff)
plt.plot(amu_seq,np.zeros(len(amu_seq)))
plt.title("Log Change in pp from Heater Install (log(After/Before))")
plt.ylabel("Log Difference in pp")

diff = np.log10(np.divide(pp_latest,pp_after))
plt.figure()
plt.plot(amu_seq,diff)
plt.plot(amu_seq,np.zeros(len(amu_seq)))
plt.title("Log Difference in pp from Baking (log(After/Before))")
plt.ylabel("Log Difference in pp")


#%%
from sklearn import preprocessing

norm = preprocessing.normalize(pp_after.reshape(1,-1))
diff = np.log10(np.divide(pp_latest,pp_after))
diff_abundance = np.multiply(diff,norm)
plt.figure()
plt.plot(amu_seq,diff_abundance[0])
plt.plot(amu_seq,np.zeros(len(amu_seq)))
plt.title("Log Difference Scaled by Abundance")
plt.ylabel("Log Difference in pp")

#%%
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
line = np.arange(0,301,10)
req = plt.plot(line[8:],np.ones(len(line[8:]))*3e-11,label='Requirement >80 amu <3E-11 Torr',c='c')
req = plt.plot(line[15:],np.ones(len(line[15:]))*3e-12,label='Requirement >150 amu <3E-12 Torr',c='m')
plt.axvline(x=80,c='c')
plt.axvline(x=150,c='m')
plt.legend()
plt.title('RGA Scan of Vacuum Chamber at 50C')
plt.xlabel('Gas Species (amu)')
plt.ylabel('Partial Pressure (log Torr)')

#%%
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

