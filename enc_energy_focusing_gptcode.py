# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 17:24:37 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
import astropy
from scipy.optimize import curve_fit
from astropy.io import fits
from matplotlib.colors import LogNorm
from matplotlib import colors
from scipy import stats
from photutils.aperture import CircularAperture, aperture_photometry, CircularAnnulus
from photutils.detection import find_peaks
from scipy.ndimage import gaussian_filter

def gaussian_2d(coords, x0, y0, sigma_x, sigma_y, amplitude, theta, offset):
    x, y = coords
    xo = float(x0)
    yo = float(y0)
    a = (np.cos(theta)**2) / (2 * sigma_x**2) + (np.sin(theta)**2) / (2 * sigma_y**2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
    c = (np.sin(theta)**2) / (2 * sigma_x**2) + (np.cos(theta)**2) / (2 * sigma_y**2)
    return offset + amplitude * np.exp(- (a * (x - xo)**2 + 2 * b * (x - xo) * (y - yo) + c * (y - yo)**2))

def measure_fwhm(image_data, x_star, y_star, box_size=20):
    # Define a small box around the star to fit the Gaussian
    x_min = int(max(x_star - box_size // 2, 0))
    x_max = int(min(x_star + box_size // 2, image_data.shape[1]))
    y_min = int(max(y_star - box_size // 2, 0))
    y_max = int(min(y_star + box_size // 2, image_data.shape[0]))
    
    sub_image = image_data[y_min:y_max, x_min:x_max]
    
    # Create a grid of coordinates
    y, x = np.mgrid[y_min:y_max, x_min:x_max]
    
    # Flatten the grid and the image data
    coords = np.vstack((x.ravel(), y.ravel()))
    sub_image_flat = sub_image.ravel()
    
    # Initial guess for the Gaussian parameters
    initial_guess = (x_star, y_star, 3, 3, np.max(sub_image), 0, np.median(sub_image))
    
    # Fit a 2D Gaussian to the star's brightness profile
    try:
        popt, _ = curve_fit(gaussian_2d, coords, sub_image_flat, p0=initial_guess)
        x0, y0, sigma_x, sigma_y, amplitude, theta, offset = popt
        
        # FWHM is related to the standard deviation by FWHM = 2.3548 * sigma
        fwhm_x = 2.3548 * sigma_x
        fwhm_y = 2.3548 * sigma_y
        fwhm = np.sqrt(fwhm_x**2 + fwhm_y**2) / np.sqrt(2)  # Average FWHM
        
        return fwhm
    except RuntimeError:
        print("Fitting failed, could not determine FWHM.")
        return None
    
def subtract_local_background(image_data, x_star, y_star, r_inner=25, r_outer=35):
    # Define an annulus around the star for background estimation
    annulus_aperture = CircularAnnulus((x_star, y_star), r_in=r_inner, r_out=r_outer)
    annulus_masks = annulus_aperture.to_mask(method='center')
    
    # Extract the background from the annulus
    annulus_data = annulus_masks.multiply(image_data)
    annulus_data_1d = annulus_data[annulus_masks.data > 0]
    
    # Estimate the background level as the median of the annulus data
    bkg_median = np.median(annulus_data_1d)
    
    # Subtract the background from the entire image
    image_data_bkg_subtracted = image_data - bkg_median
    
    return image_data_bkg_subtracted

def calculate_encircled_energy(image_data, x_star, y_star, max_radius=10):
    y, x = np.indices(image_data.shape)
    radii = np.sqrt((x - x_star)**2 + (y - y_star)**2)
    
    encircled_energy = []
    for r in range(1, max_radius + 1):
        aperture = CircularAperture((x_star, y_star), r)
        phot_table = aperture_photometry(image_data, aperture)
        encircled_energy.append(phot_table['aperture_sum'][0])
    
    encircled_energy = np.array(encircled_energy)
    encircled_energy /= encircled_energy[-1]  # Normalize by total flux
    
    return np.arange(1, max_radius + 1), encircled_energy

def plot_encircled_energy(radii, encircled_energy):
    plt.figure(figsize=(8, 6))
    plt.plot(radii, encircled_energy, marker='o', linestyle='-')
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Encircled Energy (Normalized)')
    plt.title('Encircled Energy by Radius')
    plt.grid(True)
    plt.show()
#%% Make it all happen in 1 click
'''
Requirements to Run: 
    -Photometry results from astroimageJ with name BAND_photometry_Measurements_*.csv
        You can change the * to whatever but then you will need to change it in this file
        There are 2 files below because adaptive aperture gave a better fwhm, if you do not want 2 seperate files, delete the second import
    -a folder where that photometry file and all of your desired image files are saved
    -the hexagon csv saved where it is
    
    
    NOTE the assumption about the dark current works VERY well for short exxposures
    and when we had a 10um pinhole the exposures were short (~0.1s) so you could 
    always see that asymptote to 100% if you plotted enough pixels in radius
    HOWEVER when we used the 2um pinhole that was not the case, the exposures 
    were more on the order of 10s and not having dark subtraction or bad pixel
    removal would lead to enough error that you would not see the asymptote 
    beyond ~7 pixels.
    
center    All data before 031824 was with the 2um pinhole
'''

fwhm_means=[]
fwhm_stds=[]

enc_means = []
enc_stds = []

BAND = 'NUV'#,'NUV']
if BAND == 'FUV':
    folder = ['pre_focus','minus_0.01','plus_0.01','plus_0.015','plus_0.025','final']
else:
    folder = ['pre_focus','minus_0.01','plus_0.01','plus_0.015','plus_0.025','final','final2']
    
for folder in folder:
    # path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    path = "C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase1/phase1_photosandimages/20240319/"+folder+"/"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    df = pandas.read_csv(path,delimiter=',')
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    snr = df['Source_SNR_T1']
    
    ee_darksub_array = []
    ratios_array = []
    percents_array = []
    fwhm=[]
    
    for i in np.arange(len(df)):
        row = df.iloc[i]    
        file = row['Label']
        path = "C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase1/phase1_photosandimages/20240319/"+folder+"/"+file
        image_file = astropy.io.fits.open(path, cache=True)
        image_data = fits.getdata(path)
        image_data = image_data[:,:1065]
        x = int(row['X(FITS)_T1'])
        y = int(row['Y(FITS)_T1'])
        x_star = x
        y_star = y
        fwhm.append(measure_fwhm(image_data, x, y))
        reduced_image_data = image_data
        # Step 3: Subtract the local background
        image_data_bkg_subtracted = subtract_local_background(reduced_image_data, x_star, y_star)
        # Step 4: Calculate the encircled energy
        radii, encircled_energy = calculate_encircled_energy(image_data_bkg_subtracted, x_star, y_star)
        # Step 5: Plot the encircled energy
        #plot_encircled_energy(radii, encircled_energy)    
        ee_darksub_array.append(encircled_energy)
        ratios_array.append(encircled_energy)
        percents_array.append(encircled_energy*100)
    fwhm = np.array(fwhm)

    enc_2 = []
    for i in percents_array:
        enc_2.append(i[1])
    # plt.figure()
    # plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2,s=300)
    # plt.colorbar()
    # plt.xlim((0,1175))
    # plt.ylim((0,1033))
    # plt.title(BAND+' Percent Enclosed energy in 2 pixels by field position')
    # plt.xlabel('X Pixels')
    # plt.ylabel('Y Pixels')
    
    # plt.figure()
    # plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],s=fwhm*100,c=fwhm,norm='linear',cmap='gist_rainbow')
    # plt.colorbar()
    # plt.xlim((0,1175))
    # plt.ylim((0,1033))
    # plt.title(BAND+' FWHM by field position')
    # plt.xlabel('X Pixels')
    # plt.ylabel('Y Pixels')
    
    rad = radii
    #radial field calculation
    if BAND == 'FUV':
        FOV_center = 500,500
    elif BAND == 'NUV':
        FOV_center = 500,500
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    r = np.sqrt((x-FOV_center[0])**2+(y-FOV_center[1])**2)
    r_arcmin = r*4.9/60
    # plt.figure() 
    # for i in np.arange(len(r_arcmin)):
    #     if r_arcmin[i] <= 20:
    #         plt.plot(rad*13,ratios_array[int(i)],label='Radius = '+'{:.1f}'.format(r_arcmin[i])+"'",marker='x')
    # # plt.legend()
    # # plt.plot(rad,np.mean(ratios_array,axis=0),label='Mean enclosed energy',marker='o')
    # plt.title(BAND+' Enclosed energy for all points within 40'' FOV (estimated position)')
    # plt.xlabel('Radius (um)')
    # plt.ylabel('Percent enclosed energy (%)')
    # plt.xlim((0,26))
    
    enc_means.append(np.mean(ratios_array,axis=0)) #this is what I am using to collect all of the means for later analysis
    enc_stds.append(np.std(ratios_array,axis=0))
    
    fwhm_means.append(np.mean(fwhm)) #this is what I am using to collect all of the means for later analysis
    fwhm_stds.append(np.std(fwhm))


#%%

def parabolic_function(x, a, b, c):
    return a * x**2 + b * x + c

def fit_parabola(x_data, y_data):
    # Fit the parabolic function to the data
    popt, pcov = curve_fit(parabolic_function, x_data, y_data)
    a, b, c = popt
    
    # Calculate the fitted y values
    y_fit = parabolic_function(x_data, a, b, c)
    
    # Calculate the coefficient of determination (R²)
    residuals = y_data - y_fit
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_data - np.mean(y_data))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return popt, r_squared, y_fit

def plot_fit(x_data, y_data, y_fit):
    plt.figure(figsize=(8, 6))
    plt.scatter(x_data, y_data, label='Data Points')
    plt.plot(x_data, y_fit, color='red', label='Fitted Parabola')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Parabolic Fit')
    plt.legend()
    plt.grid(True)
    plt.show()


if BAND == 'FUV':
    plt.figure()
    labels = ['Pre-focus, 0"','-0.01"','+0.01"','+0.015"','+0.025"','Final, +0.01"']
    for i in np.arange(len(enc_means)):
        plt.errorbar(rad,enc_means[i]*100,yerr=enc_stds[i]*100,fmt=':o',capsize=3,label=labels[i])
    plt.title('FUV Enclosed energy with Focusing')
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Enclosed energy (%)')
    plt.xlim(0,5)
    plt.legend()
    
    plt.figure()
    labels = ['Pre-focus, 0"','-0.01"','+0.01"','+0.015"','+0.025"','Final, +0.01"']
    x_temp = [0.0,-0.01,0.01,0.015,0.025,0.01]
    for i in np.arange(len(x_temp)):
        plt.errorbar(x_temp[i],fwhm_means[i],yerr=fwhm_stds[i],fmt='o',capsize=3,label=labels[i])
    plt.title('FUV FWHM with Focusing')
    plt.ylabel('FWHM (pixels)')
    plt.legend()
    

if BAND =='NUV':
    plt.figure()
    labels = ['Pre-focus, 0"','-0.01"','+0.01"','+0.015"','+0.025"','0"','Final, 0"']
    for i in np.arange(len(enc_means)):
        plt.errorbar(rad,enc_means[i]*100,yerr=enc_stds[i]*100,fmt=':o',capsize=3,label=labels[i])
    plt.title('NUV Enclosed energy with Focusing')
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Enclosed energy (%)')
    plt.xlim(0,5)
    plt.legend()
    
    plt.figure()
    labels = ['Pre-focus, 0"','-0.01"','+0.01"','+0.015"','+0.025"','0"','Final, 0"']
    x_temp = [0.0,-0.01,0.01,0.015,0.025,0.0,0.0]
    for i in np.arange(len(x_temp)):
        plt.errorbar(x_temp[i],fwhm_means[i],yerr=fwhm_stds[i],fmt='o',capsize=3,label=labels[i])
    plt.title('NUV FWHM with Focusing')
    plt.ylabel('FWHM (pixels)')
    # plt.legend()
    
# Example usage
Z = [x for _,x in sorted(zip(x_temp,fwhm_means))]
x_temp.sort()
x_data = np.array(x_temp)
y_data = np.array(Z)

# Fit the parabola and estimate the goodness of fit
popt, r_squared, y_fit = fit_parabola(x_data, y_data)

print(f"Fitted parameters: a = {popt[0]:.3f}, b = {popt[1]:.3f}, c = {popt[2]:.3f}")
print(f"R²: {r_squared:.3f}")

# Plot the data and the fitted parabola
# plot_fit(x_data, y_data, y_fit)

x=np.linspace(-.02,.03,1000)
y=popt[0]*x**2+popt[1]*x+popt[2]
plt.plot(x,y,'k:', label=f'Fitted Parabola R²: {r_squared:.3f}')
plt.legend()



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    