# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 14:27:45 2024

@author: logan

img = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Flats\20240712_flatattempt\20240712_142236_NUV_FFI.fits"
with fits.open(img, mode='readonly') as hdulist:
    header = hdulist[0].header
    data = hdulist[0].data
#Get the header values you need
exp = header['EXPTIME']
exposures.append(exp)

gain = header['GAIN']
gains.append(gain)


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
    
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io.fits import getdata
from astropy.io import fits
import glob
import os
from scipy import stats
from astropy.stats import sigma_clip
import pandas as pd
import glob

bias_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\0sec\*.fits"
dark_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\1800sec"
flat_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Flats\20240715_flats"


#%% Assemble a MasterBias
bias_filenames = []
bias_headers = []
bias_data = []
sigma = 5 #how many sigma to use in clipping

#load in all of the bias files
bias_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\0sec\*.fits"
for img in glob.glob(bias_folder):
    #load in the image
    bias_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        bias_headers.append(hdulist[0].header)
        bias_data.append(hdulist[0].data)

#Subtract the overscan bias 
bias_data_osub = []
overscan_medians = []
overscan_means = []
overscan_stds = []


for data in bias_data:
    #seperate out the overscan and the image
    overscan_reg = data[1:1033-8,1075:1075+96]
    image_reg = data[1:1033-8,10:10+1056]

    #sigma clip both regions to remove outliers
    overscan_clip = sigma_clip(overscan_reg,sigma=5,cenfunc='median',stdfunc='mad_std',masked=False)
    image_clip = sigma_clip(image_reg,sigma=5,cenfunc='median',stdfunc='mad_std',masked=False)

    #Calculations form the overscan
    overscan_std = np.std(overscan_clip)
    overscan_median = np.median(overscan_clip)
    overscan_medians.append(overscan_median)
    overscan_mean = np.mean(overscan_clip)
    overscan_means.append(overscan_mean)
    overscan_stds.append(overscan_stds)
    
    data_subbed = data - overscan_median
    bias_data_osub.append(data_subbed)

fuv_median_bias = np.median(bias_data_osub[:100],axis=0)
nuv_median_bias = np.median(bias_data_osub[100:],axis=0)

fuv_residual_overscan = np.median(fuv_median_bias[1:1033-8,1075:1075+96])
nuv_residual_overscan = np.median(nuv_median_bias[1:1033-8,1075:1075+96])

fuv_median_bias_residual = fuv_median_bias - fuv_residual_overscan
nuv_median_bias_residual = nuv_median_bias - nuv_residual_overscan

fuv_residual_overscan = np.median(fuv_median_bias_residual[1:1033-8,1075:1075+96]) # should be 0
nuv_residual_overscan = np.median(nuv_median_bias_residual[1:1033-8,1075:1075+96]) # should be 0

hdu = fits.PrimaryHDU(fuv_median_bias_residual)
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\FUV_masterbias.fits')

hdu = fits.PrimaryHDU(nuv_median_bias_residual)
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\NUV_masterbias.fits')


























