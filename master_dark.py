# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 14:27:45 2024

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

#load in all of the bias files
bias_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Cal_products\masterbias\*.fits"
for img in glob.glob(bias_folder):
    #load in the image
    bias_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        bias_headers.append(hdulist[0].header)
        bias_data.append(hdulist[0].data)

#%% Assemble a MasterDark
#load in all of the dark files
dark_folder = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\1800sec\*.fits"
dark_filenames = []
dark_headers = []
dark_data = []
exposures = []
gains = []
channels=[]
temps_nuv_ptc=[]
temps_nuv_plp=[]
temps_fuv_ptc=[]
temps_fuv_plp=[]


for img in glob.glob(dark_folder):
    #load in the image
    dark_filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        dark_headers.append(header)
        dark_data.append(hdulist[0].data)
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
        

fuv_index = [i for i in range(len(dark_filenames)) if 'FUV' in dark_filenames[i]]
nuv_index = [i for i in range(len(dark_filenames)) if 'NUV' in dark_filenames[i]]

#subtract the bias
dark_biassub = []
for i in np.arange(len(dark_filenames)):
    if 'FUV' in dark_filenames[i]:
        dark_biassub.append(dark_data[i]-bias_data[0])
    if 'NUV' in dark_filenames[i]:
        dark_biassub.append(dark_data[i]-bias_data[1])

#Subtract the overscan  
dark_data_biassub_osub = []
overscan_medians = []
overscan_stds = []

for data in dark_biassub:
    #seperate out the overscan and the image
    overscan_reg = data[1:1033-8,1075:1075+96]
    image_reg = data[1:1033-8,10:10+1056]

    #sigma clip both regions to remove outliers
    overscan_clip = sigma_clip(overscan_reg,sigma=5,cenfunc='median',stdfunc='mad_std',masked=False)

    #Calculations form the overscan
    overscan_std = np.std(overscan_clip)
    overscan_median = np.median(overscan_clip)
    overscan_medians.append(overscan_median)
    overscan_stds.append(overscan_std)
    
    data_subbed = data - overscan_median
    dark_data_biassub_osub.append(data_subbed)
    residual_overscan = np.median(data_subbed[1:1033-8,1075:1075+96])
    # print('Residual overscan median = {:.2f}'.format(residual_overscan))

median_fuv_dark = np.median(dark_data_biassub_osub[:nuv_index[0]],axis=0)
exposure = np.median(exposures[:nuv_index[0]])
gain = np.median(gains[:nuv_index[0]])
channel=channels[:nuv_index[0]]
nuv_ptc_temp = np.median(temps_nuv_ptc[:nuv_index[0]])
nuv_plp_temp = np.median(temps_nuv_plp[:nuv_index[0]])
fuv_ptc_temp = np.median(temps_fuv_ptc[:nuv_index[0]])
fuv_plp_temp = np.median(temps_fuv_plp[:nuv_index[0]])
median_overscan_subtracted = np.median(overscan_medians[:nuv_index[0]])
mean_overscan_std = np.mean(overscan_stds[:nuv_index[0]])*gain

image_reg = median_fuv_dark[1:1033-8,10:10+1056]
image_clip = sigma_clip(image_reg,sigma=5,cenfunc='median',stdfunc='mad_std',masked=False)
dark_counts = np.median(image_clip) #median dark count
if exposure == 0.0:
    dark_counts_s = dark_counts/1 #average dark / s
else:
    dark_counts_s = dark_counts/exposure
dark_err = stats.median_abs_deviation(image_clip)
dark_e_s = dark_counts_s * gain
median_overscan_subtracted_e = median_overscan_subtracted*gain
overscan_reg = median_fuv_dark[1:1033-8,1075:1075+96]
read_noise = np.std(overscan_reg)*gain


hdu = fits.PrimaryHDU(median_fuv_dark)
filename = 'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\FUV_mediandark_biassub_osub{:.0f}sec.fits'.format(exposure)
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\FUV_mediandark_biassub_osub{:.0f}sec.fits'.format(exposure))

d = {'Filename': filename,'Channel':channel,'Exposure (s)': exposure,
     'Gain':gain,'Median NUV Temp PTC (C)':nuv_ptc_temp,'Median NUV Temp PLP (C)':nuv_plp_temp,
     'Median FUV Temp PTC (C)':fuv_ptc_temp,'Median FUV Temp PLP (C)':fuv_plp_temp,'Median Dark Current (DN)'
     'Median Dark Rate (DN/s)':dark_counts_s,'Median Dark Rate (e-/s)':dark_e_s,'Dark Current MAD (DN)':dark_err,
     'Median Overscan Subtracted (DN)':median_overscan_subtracted,'Mean Overscan Std (e-)':mean_overscan_std, 'Final Overscan Std (e-)':read_noise}
df = pd.DataFrame(data=d)


median_nuv_dark = np.median(dark_data_biassub_osub[nuv_index[0]:],axis=0)
exposure = np.median(exposures[nuv_index[0]:])
gain = np.median(gains[nuv_index[0]:])
channel=channels[nuv_index[0]:]
nuv_ptc_temp = np.median(temps_nuv_ptc[nuv_index[0]:])
nuv_plp_temp = np.median(temps_nuv_plp[nuv_index[0]:])
fuv_ptc_temp = np.median(temps_fuv_ptc[nuv_index[0]:])
fuv_plp_temp = np.median(temps_fuv_plp[nuv_index[0]:])
median_overscan_subtracted = np.median(overscan_medians[nuv_index[0]:])
mean_overscan_std = np.mean(overscan_stds[nuv_index[0]:])*gain

image_reg = median_nuv_dark[1:1033-8,10:10+1056]
image_clip = sigma_clip(image_reg,sigma=5,cenfunc='median',stdfunc='mad_std',masked=False)
dark_counts = np.median(image_clip) #median dark count
if exposure == 0.0:
    dark_counts_s = dark_counts/1 #average dark / s
else:
    dark_counts_s = dark_counts/exposure
dark_err = stats.median_abs_deviation(image_clip)
dark_e_s = dark_counts_s * gain
median_overscan_subtracted_e = median_overscan_subtracted*gain
overscan_reg = median_nuv_dark[1:1033-8,1075:1075+96]
read_noise = np.std(overscan_reg)*gain

hdu = fits.PrimaryHDU(median_nuv_dark)
hdu.writeto(r'D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\NUV_mediandark_biassub_osub{:.0f}sec.fits'.format(exposure))
d = {'Filename': filename,'Channel':channel,'Exposure (s)': exposure,
     'Gain':gain,'Median NUV Temp PTC (C)':nuv_ptc_temp,'Median NUV Temp PLP (C)':nuv_plp_temp,
     'Median FUV Temp PTC (C)':fuv_ptc_temp,'Median FUV Temp PLP (C)':fuv_plp_temp,'Median Dark Current (DN)'
     'Median Dark Rate (DN/s)':dark_counts_s,'Median Dark Rate (e-/s)':dark_e_s,'Dark Current MAD (DN)':dark_err,
     'Median Overscan Subtracted (DN)':median_overscan_subtracted,'Mean Overscan Std (e-)':mean_overscan_std, 'Final Overscan Std (e-)':read_noise}
df.loc[1]=d
filename = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Darks\20240604_-35C_darks\outputs.csv"
df.to_csv(filename)







































