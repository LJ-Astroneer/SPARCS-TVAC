# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 16:30:15 2023

@author: Logan
"""
import csv
import numpy as np
import os
import datetime
import numpy as np

# def read_tqcm(filename):
#     path = os.path.expanduser(filename)
#     with open(path,'r', encoding='utf-8-sig', newline='') as csvfile:
#         data = list(csv.reader(csvfile))
    
#     return times, tzone1, tzone2, tzone3, tzone4, tzone5, tzone6
def read_tqcm(filename):
    path = os.path.expanduser(filename)
    with open(path,'r', encoding='utf-8-sig', newline='') as csvfile:
        text = csvfile.readlines()
    start_text = list(filter(lambda a: "Run Start Time:" in a, text))
    start_time = start_text[0][16:24]+start_text[0][44:55]
    data_text = list(text[12:])
    start = datetime.datetime.strptime(start_time,'%H:%M:%S %m-%d-%Y')
    header = list(filter(lambda a: "Time Frequency" in a, text))[0].split(' ')
    data=[]
    for line in data_text:
        line = line.split(' ')
        mins = int(line[0])
        time = start+datetime.timedelta(minutes=mins)
        time = time.strftime('%Y/%m/%d %H:%M:%S')
        line[0]=time
        data.append(line)
    data=np.asarray(data)
    return data




