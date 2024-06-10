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

pattern = "D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Darks\*\*\*.fits"
img_array = []
paths=[]
filenames = []
exposures = []
gains = []
temps = []
channels=[]
temps_nuv_ptc=[]
temps_nuv_plp=[]
temps_fuv_ptc=[]
temps_fuv_plp=[]
read_noises=[]
biases=[]
darks_counts_s=[]
darks_e_s=[]
biases_e=[]
read_noises_e=[]

for img in glob.glob(pattern):
    #load in the image
    paths.append(img)
    filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data
    
    if '_20C'in img:
        temps.append(20.0)
    if '_-32C'in img:
        temps.append(-32.0)        
    if '_-35C'in img:
        temps.append(-35.0)    
    if '_-38C'in img:
        temps.append(-38.0)    
        
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
    read_noise = np.std(overscan_clip)
    bias = np.mean(overscan_clip)
    read_noises.append(read_noise)
    biases.append(bias)
    
    #calculations from the image
    dark_counts = np.mean(image_clip-bias) #average dark count
    if exp == 0.0:
        dark_counts_s = dark_counts/1 #average dark / s
    else:
        dark_counts_s = dark_counts/exp
    dark_err = np.std(image_clip-bias)
    darks_counts_s.append(dark_counts_s)
    
    dark_e_s = dark_counts_s * gain
    bias_e = bias*gain
    read_noise_e = read_noise*gain
    darks_e_s.append(dark_e_s)
    biases_e.append(bias_e)
    read_noises_e.append(read_noise_e)
    
d = {'Filename': filenames,'Channel':channels,'Exposure (s)': exposures,
     'Gain':gains,'Setpoint Temp (°C)':temps,
     'NUV Temp PTC (°C)':temps_nuv_ptc,'NUV Temp PLP (°C)':temps_nuv_plp,
     'FUV Temp PTC (°C)':temps_fuv_ptc,'FUV Temp PLP (°C)':temps_fuv_plp,
     'Dark Current (DN/s)':darks_counts_s,'Dark Current (e-/s)':darks_e_s,
     'Bias (DN)':biases,'Bias (e-)':biases_e,'Read Noise (DN)':read_noises,
     'Read Noise (e-)':read_noises_e}
df = pd.DataFrame(data=d)
filename = "D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\\test.csv"
df.to_csv(filename)
    
    
'''
From Tahina about the actual area of the iamges to use from his understanding of the ICD
He omits the left and right column of the overscan just in case
He does not omit any of the image region


overscan_reg = dark[1:1033-8,1075:1075+96]
image_reg = dark[1:1033-8,10:10+1056]






'''


