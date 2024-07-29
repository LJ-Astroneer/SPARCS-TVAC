# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:00:54 2024

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

img = r"C:\Users\logan\Downloads\20240717_182856_FUV_FFI.fits"
with fits.open(img, mode='readonly') as hdulist:
    header = hdulist[0].header
    data = hdulist[0].data
    overscan_reg = data[1:1033-8,1075:1075+96]
    image_reg = data[1:1033-8,10:10+1056]
    
    
data=overscan_reg.flatten()

import numpy
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Define some test data which is close to Gaussian
# data = numpy.random.normal(size=10000)

hist, bin_edges = numpy.histogram(data,bins=100, density=True)
bin_centres = (bin_edges[:-1] + bin_edges[1:])/2

# Define model function to be used to fit to the data above:
def gauss(x, *p):
    A, mu, sigma = p
    return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))

# p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
p0 = [.06, 400, 20]

coeff, var_matrix = curve_fit(gauss, bin_centres, hist, p0=p0)

# Get the fitted curve
hist_fit = gauss(bin_centres, *coeff)

plt.plot(bin_centres, hist, label='Test data')
plt.plot(bin_centres, hist_fit, label='Fitted data')
plt.yscale('log')


# Finally, lets get the fitting parameters, i.e. the mean and standard deviation:
print('Fitted mean = ', coeff[1])
print('Fitted standard deviation = ', coeff[2])

plt.show()

