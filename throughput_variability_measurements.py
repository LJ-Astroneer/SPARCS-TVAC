# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 12:07:53 2024

@author: logan
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats
from scipy.optimize import curve_fit

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\variability\fuv_throughput_medians.csv")
nuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\variability\nuv_throughput_medians.csv")
photo = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\photodiode_data.csv")


#%%A better way to do things
'''
Okay so what we are going to do here instead is calculate the 'system QE' and work
with those numbers. Basically do the same thing as before but rather than use the 
normalized response actually use the calculated values for photons in the aperture
and the error to get e/p for the payload as a whole
'''

fuv_ratios = []
fuv_ratio_errors = []
for index,row in fuv.iterrows():
    incident = photo.iloc[9]['Adjusted Flux']
    inc_err = photo.iloc[9]['Adjusted Error']
    meas = row['(Source-sky)*Gain/EXP']
    meas_err = (row['Source_Error_T1']*4.2/row['EXPTIME'])
    ratio = (meas/incident)
    ratio_err = ratio*np.sqrt((meas_err/meas)**2+(inc_err/incident)**2)
    fuv_ratios.append(ratio)
    fuv_ratio_errors.append(ratio_err)

FOV_center = 500,500
r = np.sqrt((fuv['X(FITS)_T1']-FOV_center[0])**2+(fuv['Y(FITS)_T1']-FOV_center[1])**2)
fuv_r_arcmin = r*4.9/60

nuv_ratios = []
nuv_ratio_errors = []
for index,row in nuv.iterrows():
    incident = photo.iloc[52]['Adjusted Flux']
    inc_err = photo.iloc[52]['Adjusted Error']
    meas = row['(Source-sky)*Gain/EXP']
    meas_err = row['Source_Error_T1']*4.5/row['EXPTIME']
    ratio = (meas/incident)
    ratio_err = ratio*np.sqrt((meas_err/meas)**2+(inc_err/incident)**2)
    nuv_ratios.append(ratio)
    nuv_ratio_errors.append(ratio_err)
FOV_center = 500,500
r = np.sqrt((nuv['X(FITS)_T1']-FOV_center[0])**2+(nuv['Y(FITS)_T1']-FOV_center[1])**2)
nuv_r_arcmin = r*4.9/60

plt.figure()
plt.scatter(fuv['X(FITS)_T1'],fuv['Y(FITS)_T1'],c=fuv_ratios,s=300)
plt.colorbar()
plt.title('FUV Responsivity Variation with field position')
plt.xlabel('X Pixels')
plt.ylabel('Y Pixels')

plt.figure()
plt.scatter(nuv['X(FITS)_T1'],nuv['Y(FITS)_T1'],c=nuv_ratios,s=300)
plt.colorbar()
plt.title('NUV Responsivity Variation with field position')
plt.xlabel('X Pixels')
plt.ylabel('Y Pixels')

plt.figure()
plt.title('Responsivity vs. Radius from field center')
plt.xlabel('Radius (arcmin)')
plt.ylabel('Responsivity (e-/photon)')
plt.errorbar(nuv_r_arcmin,nuv_ratios,nuv_ratio_errors,fmt='o',capsize=3,label='NUV')
plt.errorbar(fuv_r_arcmin,fuv_ratios,fuv_ratio_errors,fmt='o',capsize=3,label='FUV')
plt.legend()

plt.figure()
plt.title('Responsivity vs. Radius from field center')
plt.xlabel('Radius (arcmin)')
plt.ylabel('Responsivity (e-/photon)')
plt.errorbar(nuv_r_arcmin,nuv_ratios,nuv_ratio_errors,fmt='o',capsize=3,label='NUV')
plt.errorbar(fuv_r_arcmin,fuv_ratios,fuv_ratio_errors,fmt='o',capsize=3,label='FUV')
plt.axhline(np.median(fuv_ratios)*1.1,ls=':',color='orange',label='FUV Median +/- 10%')
plt.axhline(np.median(fuv_ratios)*0.9,ls=':',color='orange')
plt.axhline(np.median(nuv_ratios)*1.1,ls=':',label='NUV Median +/- 10%')
plt.axhline(np.median(nuv_ratios)*0.9,ls=':')
plt.legend(loc='upper right')
