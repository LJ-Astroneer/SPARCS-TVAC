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

file = pd.read_csv('C:/Users/logan/Downloads/Default Dataset.csv',header=None)
file = file.to_numpy()
wv = file[:,0]
resp = file[:,1]

f = interpolate.interp1d(wv, resp)
wv_new = np.arange(int(min(wv)),int(max(wv)))
resp_new = f(wv_new)

plt.plot(wv,resp,'o')
plt.plot(wv_new, resp_new,'o')

new_data = np.array([wv_new,resp_new]).transpose()