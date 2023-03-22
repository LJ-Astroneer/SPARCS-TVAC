# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 15:50:49 2023

@author: logan
"""
import csv
import numpy as np
import os

def read_temps(filename):
    path = os.path.expanduser(filename)
    with open(path,'r', encoding='utf-8-sig', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    
    data=np.asarray(data)
    file = data[1:,0]
    times = data[1:,1]
    tzone1 = data[1:,2].astype(float)
    tzone2 = data[1:,3].astype(float)
    tzone3 = data[1:,4].astype(float)
    tzone4 = data[1:,5].astype(float)
    tzone5 = data[1:,6].astype(float)
    tzone6 = data[1:,7].astype(float)
    
    # start_head_time = datetime.strptime(times[0],'%Y-%m-%d %H:%M:%S')
    # time_list=[]
    # time_from_start = []
    # for entry in times:
    #     time_entry = datetime.strptime(entry,'%Y-%m-%d %H:%M:%S')
    #     time_list.append(time_entry)
    #     time_diff = time_entry - start_head_time
    #     sec_diff = time_diff.total_seconds()
    #     time_from_start.append(sec_diff)
    
    return file, times, tzone1, tzone2, tzone3, tzone4, tzone5, tzone6


# path = os.path.expanduser('D:/OneDrive - Arizona State University/LASI-Alpha/Documents/Sorted_data/Thermal System Zone Data/Data/2.9.23.csv')
# with open(path,'r', encoding='utf-8-sig', newline='') as csvfile:
#     data = list(csv.reader(csvfile))

# data=np.asarray(data)
# file = data[1:,0]
# times = data[1:,1]
# tzone1 = data[1:,2].astype(float)
# tzone2 = data[1:,3].astype(float)
# tzone3 = data[1:,4].astype(float)
# tzone4 = data[1:,5].astype(float)
# tzone5 = data[1:,6].astype(float)
# tzone6 = data[1:,7].astype(float)









