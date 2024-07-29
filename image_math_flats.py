# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 09:39:04 2024

@author: logan
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

bias_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\masterbias\*.fits"
for img in glob.glob(bias_folder):
    #load in the image
    bias_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        bias_headers.append(hdulist[0].header)
        bias_data.append(hdulist[0].data)

#load in master dark
dark_headers = []
dark_data = []
dark_filenames = []

dark_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\masterdark\*.fits"
for img in glob.glob(dark_folder):
    #load in the image
    dark_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        dark_headers.append(hdulist[0].header)
        dark_data.append(hdulist[0].data)

flat_headers = []
flat_data = []
flat_filenames = []
flat_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Flats\20240715_flats\*.fits"
for img in glob.glob(flat_folder):
    #load in the image
    flat_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        flat_headers.append(hdulist[0].header)
        flat_data.append(hdulist[0].data)
#%%


nuv_flats = flat_data[:5]
for i in np.arange(len(nuv_flats)):
    bias_sub = nuv_flats[i] - bias_data[1]
    overscan_reg = bias_sub[1:1033-8,1075:1075+96]
    bias_sub_osub = bias_sub - np.median(overscan_reg)
    dark_sub = bias_sub_osub - (dark_data[1]*600)
    hdu = fits.PrimaryHDU(dark_sub)
    name = flat_filenames[i]
    hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\reduced\\'+name)


nuv_flats = flat_data[:5]
nuv_flats_bias_sub_osub=[]
for i in np.arange(len(nuv_flats)):
    bias_sub = nuv_flats[i] - bias_data[1]
    overscan_reg = bias_sub[1:1033-8,1075:1075+96]
    bias_sub_osub = bias_sub - np.median(overscan_reg)
    nuv_flats_bias_sub_osub.append(bias_sub_osub)
median_nuv_flat = np.median(nuv_flats_bias_sub_osub,axis=0)
dark_sub = median_nuv_flat - (dark_data[1]*600)
hdu = fits.PrimaryHDU(dark_sub)
name = 'nuv_flat_median_biassub_osub.fits'
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\reduced\\'+name)

bias_sub = flat_data[5] - bias_data[0]
overscan_reg = bias_sub[1:1033-8,1075:1075+96]
bias_sub_osub = bias_sub - np.median(overscan_reg)
dark_sub = bias_sub_osub - (dark_data[0]*3600)
hdu = fits.PrimaryHDU(dark_sub)
name = flat_filenames[5]
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\reduced\\'+name)
















