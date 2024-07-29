# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 09:29:40 2024

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

pattern = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\20240722_readnoise\*NUV*fits"
filenames = []
nuv_biases = []
nuv_read_noises = []
for img in glob.glob(pattern):
    #load in the image
    filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data
        
        #seperate out the overscan and the image
        overscan_reg = data[1:1033-8,1075:1075+96]
        image_reg = data[1:1033-8,10:10+1056]
        
        #sigma clip both regions to remove outliers
        overscan_clip,over_high,over_low = stats.sigmaclip(overscan_reg,5,5)
        image_clip,image_high,image_low = stats.sigmaclip(image_reg,5,5)
        
        #Calculations form the overscan
        read_noise = np.std(overscan_clip)*4.5
        bias = np.mean(overscan_clip)*4.5
        nuv_read_noises.append(read_noise)
        nuv_biases.append(bias)
        
pattern = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\20240722_readnoise\*FUV*fits"
filenames = []
fuv_biases = []
fuv_read_noises = []
for img in glob.glob(pattern):
    #load in the image
    filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data
        
        #seperate out the overscan and the image
        overscan_reg = data[1:1033-8,1075:1075+96]
        image_reg = data[1:1033-8,10:10+1056]
        
        #sigma clip both regions to remove outliers
        overscan_clip,over_high,over_low = stats.sigmaclip(overscan_reg,5,5)
        image_clip,image_high,image_low = stats.sigmaclip(image_reg,5,5)
        
        #Calculations form the overscan
        read_noise = np.std(overscan_clip)*4.2
        bias = np.mean(overscan_clip)*4.2
        fuv_read_noises.append(read_noise)
        fuv_biases.append(bias)
        

#%%
fig, ax = plt.subplots()
i = np.arange(len(nuv_read_noises))
ax.plot(nuv_read_noises,'-or',label='NUV')
ax.plot(fuv_read_noises,'-ob',label='FUV')
mi = np.min(nuv_read_noises+fuv_read_noises)
mx = np.max(nuv_read_noises+fuv_read_noises)
ax.fill_betweenx([mi,mx],0,4, facecolor='g', alpha=.5,label='Control')
ax.fill_betweenx([mi,mx],5,9, facecolor='b', alpha=.5,label='Grounded')
ax.fill_betweenx([mi,mx],10,14, facecolor='r', alpha=.5,label='Ground+Toroid')
ax.fill_betweenx([mi,mx],15,19, facecolor='y', alpha=.5,label='Grounded repeat')
ax.fill_betweenx([mi,mx],20,24, facecolor='m', alpha=.5,label='Grounded repeat2')
ax.fill_betweenx([mi,mx],25,29, facecolor='c', alpha=.5,label='PTC Off')
ax.set_ylabel('Read Noise (e)')
plt.legend()
plt.show()  
  
  
#%%
pattern = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\20240722_readnoise\longer_exp\*NUV*fits"
filenames = []
nuv_biases = []
nuv_read_noises = []
for img in glob.glob(pattern):
    #load in the image
    filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data
        
        #seperate out the overscan and the image
        overscan_reg = data[1:1033-8,1075:1075+96]
        image_reg = data[1:1033-8,10:10+1056]
        
        #sigma clip both regions to remove outliers
        overscan_clip,over_high,over_low = stats.sigmaclip(overscan_reg,5,5)
        image_clip,image_high,image_low = stats.sigmaclip(image_reg,5,5)
        
        #Calculations form the overscan
        read_noise = np.std(overscan_clip)*4.5
        bias = np.mean(overscan_clip)*4.5
        nuv_read_noises.append(read_noise)
        nuv_biases.append(bias)
        
pattern = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\20240722_readnoise\longer_exp\*FUV*fits"
filenames = []
fuv_biases = []
fuv_read_noises = []
for img in glob.glob(pattern):
    #load in the image
    filenames.append(os.path.basename(img))
    with fits.open(img, mode='readonly') as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data
        
        #seperate out the overscan and the image
        overscan_reg = data[1:1033-8,1075:1075+96]
        image_reg = data[1:1033-8,10:10+1056]
        
        #sigma clip both regions to remove outliers
        overscan_clip,over_high,over_low = stats.sigmaclip(overscan_reg,5,5)
        image_clip,image_high,image_low = stats.sigmaclip(image_reg,5,5)
        
        #Calculations form the overscan
        read_noise = np.std(overscan_clip)*4.2
        bias = np.mean(overscan_clip)*4.2
        fuv_read_noises.append(read_noise)
        fuv_biases.append(bias)
          
#%%
fig, ax = plt.subplots()
i = np.arange(len(nuv_read_noises))
ax.plot(nuv_read_noises,'-or',label='NUV')
ax.plot(fuv_read_noises,'-ob',label='FUV')
mi = np.min(nuv_read_noises+fuv_read_noises)
mx = np.max(nuv_read_noises+fuv_read_noises)
ax.set_ylabel('Read Noise (e)')
ax.fill_betweenx([mi,mx],0,4, facecolor='g', alpha=.5,label='0 sec')
ax.fill_betweenx([mi,mx],5,9, facecolor='b', alpha=.5,label='1 sec')
ax.fill_betweenx([mi,mx],10,14, facecolor='r', alpha=.5,label='10 sec')
plt.legend()
plt.show()    
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  