# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:26:15 2024

@author: logan
"""
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
from scipy import stats
from scipy import interpolate
import math

import imageio as iio

img = iio.imread('D:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/BeamCalibrationImages/PXL_20240521_211858000.RAW-01.MP.COVER.jpg')
img_g = img[:,:,1] #this is the green channel
img_crop = img_g[1800:2700,1300:2200]

index = np.where(img_crop >= 80) #setting a cutoff level we want pixels above
index2 = np.where(img_crop < 80)
temp = np.copy(img_crop)
temp[index] = 1
temp[index2] = 0
plt.imshow(temp) #removed pixels not bright enough


#%%
temp2 = np.copy(temp)
ctr_y,ctr_x = 450,435
#inner_rad = (ctr_x-i)**2+(ctr_y-j)**2
for i in np.arange(len(temp[0])):
    for j in np.arange(len(temp[1])):
        if np.sqrt((ctr_x-i)**2+(ctr_y-j)**2) < 200:
            temp2[i,j] = 0
plt.imshow(temp2) #remove pixels inside the shadow

ctr_y,ctr_x = 465,430
temp3 = np.copy(temp2)
for i in np.arange(len(temp[0])):
    for j in np.arange(len(temp[1])):
        if np.sqrt((ctr_x-i)**2+(ctr_y-j)**2) > 435:
            temp3[i,j] = 0
plt.imshow(temp3) #remove pixels outside the beam

temp4 = np.copy(temp3)
temp4[:,796:] = 0
plt.imshow(temp4) #removed the remaining pixels outside

#%%
count = np.sum(temp4)
print('Number of pixels in beam = {:.0f}'.format(count))

area = count*0.114**2 #mm^2/pixel
print('Estimated beam area = {:.2f} mm^2'.format(area))






