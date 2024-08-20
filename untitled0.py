# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 12:07:53 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_combined_throughput_median.csv")
nuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\nuv_combined_throughput_median.csv")

fuv_err = fuv['Source_Error_T1']*4.2/fuv['EXPTIME']
nuv_err = nuv['Source_Error_T1']*4.2/nuv['EXPTIME']

plt.errorbar(fuv['Wavelength (nm)'],fuv['(Source-sky)*Gain/EXP'],fuv_err,8/2.355,fmt='-o',capsize=4) #the bandpass is 8nm FWHM so to std dev is FWHM/2.355
plt.errorbar(nuv['Wavelength (nm)'],nuv['(Source-sky)*Gain/EXP'],nuv_err,8/2.355,fmt='-o',capsize=4) #the bandpass is 8nm FWHM so to std dev is FWHM/2.355
plt.yscale('log')
plt.title('Measured intensity vs Wavelength')
plt.ylabel('Intensity (e-/s)')
plt.xlabel('Wavelength (nm)')

