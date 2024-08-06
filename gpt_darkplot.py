# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:26:15 2024

@author: logan
"""
import numpy as np
import matplotlib.pyplot as plt
from astropy.io.fits import getdata
from astropy.io import fits
import glob
import os
from scipy import stats
import pandas as pd

pattern = "D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darksandbiases\*\output\*dark*"
img_array = []
paths=[]
filenames = []
exposures = []
gains = []
channels=[]
temps_nuv_ptc=[]
temps_nuv_plp=[]
temps_fuv_ptc=[]
temps_fuv_plp=[]
darks_counts_s=[]
darks_e_s=[]
darks_err = []
darks_err_e =[]
medians = []
medians_e=[]
mads = []
mads_e = []

for img in glob.glob(pattern):
    #load in the image
    paths.append(os.path.dirname(img))
    filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data

    #Get the header values you need
    exp = header['EXPTIME']
    exposures.append(exp)
    
    gain = header['GAIN']
    gains.append(gain)
    
    temp_nuv_ptc=header['T_NUV_PT']
    temp_nuv_plp=header['T_NUV_PL']
    temp_fuv_ptc=header['T_FUV_PT']
    temp_fuv_plp=header['T_FUV_PL']
    temps_nuv_ptc.append(temp_nuv_ptc)
    temps_nuv_plp.append(temp_nuv_plp)
    temps_fuv_ptc.append(temp_fuv_ptc)
    temps_fuv_plp.append(temp_fuv_plp)
    
    channels.append(header['CHANNEL'])
    
    #seperate out the overscan and the image
    overscan_reg = data[1:1033-8,1075:1075+96]
    image_reg = data[1:1033-8,10:10+1056]
    
    #sigma clip both regions to remove outliers
    overscan_clip,over_high,over_low = stats.sigmaclip(overscan_reg,5,5)
    image_clip,image_high,image_low = stats.sigmaclip(image_reg,5,5)
    
    #Calculations form the overscan

    
    #calculations from the image
    dark_counts = np.mean(image_clip) #average dark count
    if exp == 0.0:
        exp = 1.0
    dark_counts_s = dark_counts/exp
    med = np.median(image_reg)/exp
    mad = stats.median_abs_deviation(image_reg.flatten())/exp
    dark_err = np.std(image_clip)/exp
    
    darks_counts_s.append(dark_counts_s)
    dark_err_e = dark_err*gain
    dark_e_s = dark_counts_s * gain
    darks_e_s.append(dark_e_s)
    darks_err.append(dark_err)
    darks_err_e.append(dark_err_e)
    
    med_e = med*gain
    medians.append(med)
    medians_e.append(med_e)

    mad_e = mad*gain
    mads.append(mad)
    mads_e.append(mad_e)
    
    
    
d = {'Folder':paths, 'Filename': filenames,'Channel':channels,'Exposure (s)': exposures,
      'Gain':gains,'NUV Temp PTC (°C)':temps_nuv_ptc,'NUV Temp PLP (°C)':temps_nuv_plp,
      'FUV Temp PTC (°C)':temps_fuv_ptc,'FUV Temp PLP (°C)':temps_fuv_plp,
      'Dark Current (DN/s)':darks_counts_s,'Dark Current (e-/s)':darks_e_s,
      'Dark Std.Dev (DN/s)':darks_err,'Dark Std.Dev (e-/s)':darks_err_e,
      'Median (DN/s)':medians,'Median(e-/s)':medians_e,'MAD (DN/s)':mads,'MAD (e-/s)':mads_e}
df = pd.DataFrame(data=d)
filename = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darksandbiases\test.csv"
df.to_csv(filename)


#%%
labels = ['20C FUV','20C NUV','-32C FUV','-32V NUV','-35C FUV','-35C NUV','-38C FUV','-38C NUV']
plt.figure()
for i in np.arange(2,len(labels)):
    exp = exposures[i*6:(i*6)+6]
    d = darks_e_s[i*6:(i*6)+6]
    err = darks_err_e[i*6:(i*6)+6]
    # plt.plot(exp,d,'o',label=labels[i])
    plt.errorbar(exp, d, yerr=err,fmt='o',label=labels[i],capsize=3)
plt.legend()  
  
plt.figure()
for i in np.arange(2,len(labels)):
    exp = exposures[i*6:(i*6)+6]
    d = medians_e[i*6:(i*6)+6]
    err = mads_e[i*6:(i*6)+6]
    # plt.plot(exp,d,'o',label=labels[i])
    plt.errorbar(exp, d, yerr=err,fmt='o',label=labels[i],capsize=3)
plt.legend()  
