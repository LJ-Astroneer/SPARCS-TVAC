# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:26:15 2024

@author: logan
"""
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
from scipy import stats
from scipy import interpolate
import math

file = pd.read_csv('C:/Users/logan/Downloads/extracted_data.csv',header=None)
file = file.to_numpy()
ev = file[:,0]
resp = file[:,1]

conv = 1.602176634e-19 #J / Ev
h=6.62607015e-34 #J s
c=299792458 #m/s

wv = (h/conv*c)*1e9/ev

f = interpolate.interp1d(wv, resp)
wv_new = np.arange(math.ceil(min(wv)),math.floor(max(wv)))
resp_new = f(wv_new)

plt.plot(wv,resp,'o')
plt.plot(wv_new, resp_new,'o')

new_data = np.array([wv_new,resp_new]).transpose()