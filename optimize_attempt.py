# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 16:24:11 2020

@author: logan
"""
import os
import pandas as pd
import glob
import csv
import numpy as np

path = os.path.abspath('/Users/logan/Google Drive/RGA_data/11.20')
all_files = glob.glob(os.path.join(path, "*.csv"))

file = []
str_file = []
with open(all_files[0], 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for i, elem in enumerate(csv_file):
        if 'PiraniPressureOut' in elem:
            p_i = i
        if '</ConfigurationData>' in elem:
            start = i+1

def readfile(file):
    df = pd.read_csv(all_files[0],skiprows=start,header=None,
     names=['datetime','amu','pp'],index_col=False,parse_dates=['datetime'],
     dtype={'amu':np.float64,'pp':np.float64})
    return df
df = pd.concat(readfile(f) for f in all_files)
#df = pd.concat((pd.read_csv(f) for f in all_files))
# #df = pd.read_csv(all_files[0],skiprows=start,header=None,
#      names=['datetime','amu','pp'],index_col=False,parse_dates=['datetime'],
#      dtype={'amu':np.float64,'pp':np.float64})
