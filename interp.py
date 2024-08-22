# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:26:36 2024

@author: logan
"""

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import pandas as pd
import csv
from scipy.optimize import curve_fit

fuv_qe = pd.read_csv(r'D:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/Throughput/QE from JPL/JPL_FUV_raw.csv')
# Example sporadic dataset
x = fuv_qe['wav[nm]']
y = fuv_qe['avg QE [%]']
# Create an interpolation function
interp_function = interp1d(x, y, kind='cubic')  # 'linear', 'quadratic', and 'cubic' are common choices for 'kind'

# Generate new x values for interpolation
x_new = np.arange(x.min(), x.max())  # 500 points between min and max of x

# Use the interpolation function to calculate new y values
y_new = interp_function(x_new)
plt.figure()
plt.scatter(x, y, color='red', label='Original Data')
plt.plot(x_new, y_new, color='blue', label='Interpolated Data')
plt.legend()
plt.show()
