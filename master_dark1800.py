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

#load in master bias
bias_headers = []
bias_data = []
bias_filenames = []

#load in all of the bias files
bias_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\masterbias\*.fits"
for img in glob.glob(bias_folder):
    #load in the image
    bias_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        bias_headers.append(hdulist[0].header)
        bias_data.append(hdulist[0].data)

#%% Assemble a MasterDark
dark_filenames = []
dark_headers = []
dark_data = []
sigma = 5 #how many sigma to use in clipping

#load in all of the dark files
dark_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\1800sec\*.fits"
for img in glob.glob(dark_folder):
    #load in the image
    dark_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        dark_headers.append(hdulist[0].header)
        dark_data.append(hdulist[0].data)

'''
in here somehwere you would want to have your averaging of the darks together, but since we only 
have 1 1800s image then we cannot do any of that
'''
#subtract the bias
fuv_dark_biassub = dark_data[0]-bias_data[0]
nuv_dark_biassub = dark_data[1]-bias_data[1]



#Subtract the overscan dark 
dark_data_osub = []
overscan_medians = []
overscan_stds = []

for data in dark_data:
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
    overscan_stds.append(overscan_stds)
    
    data_subbed = data - overscan_median
    dark_data_osub.append(data_subbed)

fuv_residual_overscan = np.median(dark_data_osub[0][1:1033-8,1075:1075+96])
print('FUV residual overscan median = {:.2f}'.format(fuv_residual_overscan))
nuv_residual_overscan = np.median(dark_data_osub[1][1:1033-8,1075:1075+96])
print('NUV residual overscan median = {:.2f}'.format(nuv_residual_overscan))

fuv_dark_norm = dark_data_osub[0]/1800
nuv_dark_norm = dark_data_osub[1]/1800


# hdu = fits.PrimaryHDU(fuv_dark_norm)
# hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\FUV_masterdark.fits')

# hdu = fits.PrimaryHDU(nuv_dark_norm)
# hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\NUV_masterdark.fits')

hdu = fits.PrimaryHDU(fuv_dark_norm*7200)
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\FUV_masterdark_7200s.fits')

hdu = fits.PrimaryHDU(nuv_dark_norm*600)
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\NUV_masterdark_600s.fits')

























