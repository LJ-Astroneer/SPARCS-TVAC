# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:02:29 2024

@author: logan
"""
#Packages
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.io import fits
from matplotlib.colors import LogNorm
import os
from scipy.interpolate import UnivariateSpline

#loading in a file
path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240220\MED_FUV_0nm_darksub.fits"
image_file = astropy.io.fits.open(path, cache=True)
image_data = fits.getdata(path)

#plotting
plt.imshow(image_data,cmap='gray')
plt.colorbar()

#stats
print('Min:', np.min(image_data))
print('Max:', np.max(image_data))
print('Mean:', np.mean(image_data))
print('Stdev:', np.std(image_data))

#histogram
histogram = plt.hist(image_data.flatten(), bins='auto')

#plot with log scale
plt.imshow(image_data, cmap='gray', norm=LogNorm())

#image stacking
path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240213\3 minute\NUV_pinhole"
path = os.path.abspath(path)
image_list = [(os.path.join(path,image)) for image in os.listdir(path)]  
image_concat = [fits.getdata(image) for image in image_list]
final_image = np.sum(image_concat, axis=0)
image_hist = plt.hist(final_image.flatten(), bins='auto')

filename = 'stacked_image.fits'
outfile = os.path.join(path,filename)
hdu = fits.PrimaryHDU(final_image)
hdu.writeto(outfile, overwrite=True)

#%%
def profiles(image_data):
    pinhole_center = np.where((image_data == np.max(image_data)))
    x = np.take(image_data, pinhole_center[1][0], axis=1)
    y = np.take(image_data, pinhole_center[0][0], axis=0)

    return x, y #these are the horizontal and vertical profiles through the star's centroid

def interpolate_width(axis):
    half_max = 1/2*np.max(axis)
    x = np.linspace(0, len(axis), len(axis))

    # Do the interpolation
    spline = UnivariateSpline(x, axis-half_max, s=0)
    r1, r2 = spline.roots()[0], spline.roots()[-1]

    return r2-r1 #this is the FWHM along the specified axis


path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240221\MED_NUV_2um.fits"
image_file = astropy.io.fits.open(path, cache=True)
image_data = fits.getdata(path)

horizontal, vertical = profiles(image_data)
fwhm_x = interpolate_width(horizontal)
fwhm_y = interpolate_width(vertical)
Error_approx = abs(fwhm_x-fwhm_y)
print(fwhm_x,fwhm_y)
print('FWHM is {:.2f} with an error of {:.2f}'.format(np.median([fwhm_x,fwhm_y]),Error_approx))















