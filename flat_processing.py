# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 12:06:42 2022

@author: logan
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

path = r'C:\Users\logan\Videos\Bench_flats'
path = os.path.abspath(path)
folder = os.listdir(path) 
stack = []    
for entry in folder:
    im = Image.open(path+'\\'+entry)
    imarray = np.array(im)
    stack.append(imarray)

median_image = np.median(stack,axis=0)
plt.figure()
plt.imshow(median_image,cmap='Greys_r')
plt.colorbar()
plt.title('Median Flat')

median = np.median(stack)
master_flat = median_image/median
plt.figure()
plt.imshow(master_flat,cmap='Greys_r')
plt.colorbar()
plt.title('Master Flat')

median_row = np.median(master_flat,axis=1)
median_column = np.median(master_flat,axis=0)
plt.figure()
plt.scatter(np.arange(0,len(median_row)),median_row)
plt.scatter(np.arange(0,len(median_column)),median_column)
plt.legend(['Median by Row','Median by Column'])

plt.figure()
listed = master_flat.flatten().tolist()
plt.hist(listed,20,log="True")

plt.figure()
plt.imshow(master_flat,cmap='Greys_r',vmin=0.97,vmax=1.03)
plt.colorbar()
plt.title('Master Flat')

mf_tiff = Image.fromarray(master_flat)
mf_tiff.save(path+'\\'+'master_flat')











