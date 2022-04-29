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

for test in range(14):
    path = os.path.abspath('/Users/logan/Desktop/Grad_School/RGA_data/10.15_leaktest')
    # test = input("Which Test to plot? 0-13:     ")
    entry = os.listdir(path)[int(test)]
    
    pirani = []
    totalp = []
    data = []
    
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
    for row in data:
        times.append(row[0])
        amu.append(row[1])
        pp.append(row[2])
        x+=1
    amu = np.asarray(amu)
    amu = amu.astype(np.float64)
    pp = np.asarray(pp)
    pp  = pp.astype(np.float64)
    
    
    #%% Sort the values
    he_i = np.where(amu ==4)
    n2_i = np.where(amu == 28)
    o2_i = np.where(amu == 32)
    pirani_i = np.where(amu == 5)
    total_i = np.where(amu == 999)
    
    start_time = datetime.strptime(times[0],'%Y/%m/%d %H:%M:%S.%f')
    time_from_start = []
    for t in times:
        time = datetime.strptime(t,'%Y/%m/%d %H:%M:%S.%f')
        time_diff = time - start_time
        sec_diff = time_diff.total_seconds()
        time_from_start.append(sec_diff)
    time_from_start = np.array(time_from_start)
    hours_from_start = np.divide(time_from_start,3600)
    
    he_time = time_from_start[he_i]
    n2_time = time_from_start[n2_i]
    o2_time = time_from_start[o2_i]
    pirani_time = time_from_start[pirani_i]
    total_time = time_from_start[total_i]
    
    he = pp[he_i]/1000 #gain from EM is 1000
    n2 = pp[n2_i]/1000
    o2 = pp[o2_i]/1000
    pirani = pp[pirani_i]
    total = pp[total_i]
    
    plt.figure()
    plt.semilogy(he_time,he,n2_time,n2,o2_time,o2,total_time,total)
    plt.title("Leak Test {}".format(int(test)+1))
    plt.ylabel("Log (Torr)")
    plt.xlabel("Seconds")
    plt.legend(['He','N2','O2','Total Press'])
    plt.savefig('leak_test_{}'.format(int(test)+1))
















