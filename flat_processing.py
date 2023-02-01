# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 12:06:42 2022

@author: Logan Jensen
Used as a quick way to read all the flats in and do some math using the
Python imaging library. Note that I did not write this with functions, but 
did break it into cells so if you are using Spyder you can just run a cell.
too lazy for functions
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
'''
you need to change the path to wherever your images are. NOTE that every file in 
the folder you put will be read into the program, so make sure the only thing in there
are the images you want to process.
'''
path = r'C:\Users\logan\Videos\Bench_flats'
path = os.path.abspath(path) #converts the path to something your computer understands
folder = os.listdir(path) 
stack = [] #the stack of images, this will be a list of arrays    
for entry in folder: #loads all of the images with PIL
    im = Image.open(path+'\\'+entry)
    imarray = np.array(im)
    stack.append(imarray)

#%%
#calculates the median image of all the images in the array then plots it with a colorbar
median_image = np.median(stack,axis=0)
plt.figure()
plt.imshow(median_image,cmap='Greys_r')
plt.colorbar()
plt.title('Median Flat')

#%%
'''
This creates what is called the Master Flat, you find the median value for all
of the pixels in the stack then divide the median image by the median value 
(could also take the median of the median image, but whatever). That is how you
normalize the image to 1 creating a master flat.
'''
median = np.median(stack)
master_flat = median_image/median
plt.figure()
plt.imshow(master_flat,cmap='Greys_r')
plt.colorbar()
plt.title('Master Flat')

#%%
#this plots the median values of each row and column to look for gradients
#note that the bench detector is 1080x1440, the SPARCS one will be 1000x1000
median_row = np.median(master_flat,axis=1)
median_column = np.median(master_flat,axis=0)
plt.figure()
plt.scatter(np.arange(0,len(median_row)),median_row)
plt.scatter(np.arange(0,len(median_column)),median_column)
plt.legend(['Median by Row','Median by Column'])

#%%
#This makes a histogram of all the pixel values in the master_flat
#should always be like a gaussian(ish) centered around 1
plt.figure()
listed = master_flat.flatten().tolist()
plt.hist(listed,20,log="True")

#%%
#This one makes a really high contrast image like you could do in imageJ
#uses the medians of the rows and columns as the max and min values in the image
minimum = min(np.append(median_row,median_column))
maximum = max(np.append(median_row,median_column))
plt.figure()
plt.imshow(master_flat,cmap='Greys_r',vmin=minimum,vmax=maximum)
plt.colorbar()
plt.title('Master Flat')

mf_tiff = Image.fromarray(master_flat)
mf_tiff.save(path+'\\'+'master_flat.tiff')











