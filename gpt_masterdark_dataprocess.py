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

pattern = "D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darkandbias_overscan2.1\*\output\*dark*"
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
medians_s = []
medians_e_s=[]
mads = []
mads_e = []
totals=[]

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
    med = np.median(image_clip)
    med_s = med/exp
    mad = stats.median_abs_deviation(image_clip.flatten())/exp
    dark_err = np.std(image_clip)/exp
    
    darks_counts_s.append(dark_counts_s)
    dark_err_e = dark_err*gain
    dark_e_s = dark_counts_s * gain
    darks_e_s.append(dark_e_s)
    darks_err.append(dark_err)
    darks_err_e.append(dark_err_e)
    
    med_e = med*gain
    med_e_s = med_e/exp
    medians.append(med)
    medians_e.append(med_e)
    medians_s.append(med_s)
    medians_e_s.append(med_e_s)

    mad_e = mad*gain
    mads.append(mad)
    mads_e.append(mad_e)
    totals.append(np.sum(image_clip)*gain)
    
    
d = {'Folder':paths, 'Filename': filenames,'Channel':channels,'Exposure (s)': exposures,
      'Gain':gains,'NUV Temp PTC (°C)':temps_nuv_ptc,'NUV Temp PLP (°C)':temps_nuv_plp,
      'FUV Temp PTC (°C)':temps_fuv_ptc,'FUV Temp PLP (°C)':temps_fuv_plp,
      'Mean DC Rate (DN/s)':darks_counts_s,'Mean DC Rate (e-/s)':darks_e_s,
      'Rate Std.Dev (DN/s)':darks_err,'Rate Std.Dev (e-/s)':darks_err_e,
      'Median DC Rate (DN/s)':medians_s,'Median DC Rate (e-/s)':medians_e_s,
      'Rate MAD (DN/s)':mads,'Rate MAD (e-/s)':mads_e,'Total Dark (e-)':totals}
df = pd.DataFrame(data=d)
df = df.sort_values(by=['Folder','Exposure (s)'])
filename = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darkandbias_overscan2.1\dark.csv"
df.to_csv(filename)