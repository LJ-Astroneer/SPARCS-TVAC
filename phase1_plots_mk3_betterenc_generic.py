# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:06:20 2024

@author: logan


The purpose of this code is to take the data specifically from 20240222 and make plots from it.  Returns plots of the FWHM and Encircled energy distributions across the detectors, both as scatter plots with colorbars, interpolated mesh heatmaps, and a 2d scatter plot with error bars.

NOTE: For this function to work you need a measuremnt file from AstroimageJ's multiaperture routine that I used to measure the X and Y corrdinate for each star position and the name of the image file. 

Requirements to Run: 
    -Photometry results from astroimageJ with name BAND_photometry_Measurements_*.csv
        You can change the * to whatever but then you will need to change it in this file
        There are 2 files below because adaptive aperture gave a better fwhm, if you do not want 2 seperate files, delete the second import
    -a folder where that photometry file and all of your desired image files are saved
    -the hexagon csv saved where it is
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
from scipy.interpolate import griddata

'''
fitting a 2D gaussian function to feed into the curve_fit program that will be used to measure the FWHM
'''
def gaussian_2d(coords, x0, y0, sigma_x, sigma_y, amplitude, theta, offset):
    x, y = coords
    xo = float(x0)
    yo = float(y0)
    a = (np.cos(theta)**2) / (2 * sigma_x**2) + (np.sin(theta)**2) / (2 * sigma_y**2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
    c = (np.sin(theta)**2) / (2 * sigma_x**2) + (np.cos(theta)**2) / (2 * sigma_y**2)
    return offset + amplitude * np.exp(- (a * (x - xo)**2 + 2 * b * (x - xo) * (y - yo) + c * (y - yo)**2))

'''
Measuring the FWHM by taking a subsection of the image around the star and then fitting a 2D gaussian to the data in the box to then measure the FWHM. The average FWHM returned is from adding the X-FWHM and Y-FWHM in quadrature.
'''
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

'''
This is the equivalent for dark correction for this image set in using an annulus around the defined star in the image to estiamte a median background value and subtracting that value from the image. 
'''
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

'''
A better solution to calculating the encircled energy than what I was doing initially. This program uses the photutils package properly to evaluate the encircled energy distribution around a star.
'''
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

folder = input("What folder you want?! (20240222) \n")
means = []
BANDS = ['FUV','NUV']
for BAND in BANDS:
    path = r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    df = pandas.read_csv(path,delimiter=',')
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    snr = df['Source_SNR_T1']
    
    ee_darksub_array = []
    ratios_array = []
    percents_array = []
    fwhm = []
    
    for i in np.arange(len(df)):
        row = df.iloc[i]    
        file = row['Label']
        path = r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+file
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
    
        # ee_darksub_array.append(ee_darksub)
        # ratios_array.append(ratios)
        # percents_array.append(percents)
    fwhm = np.array(fwhm)
    enc_2 = []
    for i in percents_array:
        enc_2.append(i[1])
    plt.figure()
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2,s=300)
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+' Percent Enclosed energy in 2 pixels by field position')
    plt.xlabel('X Pixels')
    plt.ylabel('Y Pixels')
    
    plt.figure()
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],s=fwhm*100,c=fwhm,norm='linear',cmap='gist_rainbow')
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+' FWHM by field position')
    plt.xlabel('X Pixels')
    plt.ylabel('Y Pixels')
    #%% Going to try to make the above into a surface
    '''
    So this does technically work but it is a stretch at best. You only have 80 sample points
    for a really large array. Honeslty looking back at it now we probably should have
    taken a more dense sample, but I suppose the point is just to understand the
    behavior in the FOV of interest.
    
    Anyway what this does is makes a grid of points the size of the whole image,
    then you feed it the values you know at the points you know them. Then griddata
    interpolates the values to fill in all of the other pixels with whatever method
    you want.
    
    This function runs on every individual measurement from the above loading function so it is not recommmended for 20240322 since it works best with the combination of the 5 measuremetns at each location
    '''

    # 
    grid_x, grid_y = np.mgrid[:1033, :1175]
    points = (np.array((df['Y(FITS)_T1'],df['X(FITS)_T1']))).transpose() #flipped x and y here because I had to for it to work
    values = np.array(fwhm)
    grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')
    
    plt.figure()
    plt.subplot(221)
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=fwhm,cmap='viridis_r')
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+'Data Acquired')
    plt.subplot(222)
    plt.imshow(grid_z0,origin='lower',cmap='viridis_r')
    plt.colorbar()
    plt.title('Nearest')
    plt.subplot(223)
    plt.imshow(grid_z1,origin='lower',cmap='viridis_r')
    plt.colorbar()
    plt.title('Linear')
    plt.subplot(224)
    plt.imshow(grid_z2,origin='lower',cmap='viridis_r')
    plt.colorbar()
    plt.title('Cubic')
    plt.suptitle(BAND+' FWHM mesh interpolation')
    plt.show()
    
    grid_x, grid_y = np.mgrid[:1033, :1175]
    points = (np.array((df['Y(FITS)_T1'],df['X(FITS)_T1']))).transpose() #flipped x and y here because I had to for it to work
    values = np.array(enc_2)
    grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')
    
    plt.figure()
    plt.subplot(221)
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2)
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+'Data Acquired')
    plt.subplot(222)
    plt.imshow(grid_z0,origin='lower')
    plt.colorbar()
    plt.title('Nearest')
    plt.subplot(223)
    plt.imshow(grid_z1,origin='lower')
    plt.colorbar()
    plt.title('Linear')
    plt.subplot(224)
    plt.imshow(grid_z2,origin='lower')
    plt.colorbar()
    plt.title('Cubic')
    plt.suptitle(BAND+' Encirncled Energy mesh interpolation')
    plt.show()
    
    
    #%%
    '''
    This function plots the encircled energy distribution measured and compares it to the hexagon data. This again runs for every single measurement taken form all of the files and so for the 20240322 folder there would be an excessive amount of plots that are not needed.
    '''
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
    plt.figure() 
    for i in np.arange(len(r_arcmin)):
        if r_arcmin[i] <= 20:
            plt.plot(rad*13,ratios_array[int(i)],label='Radius = '+'{:.1f}'.format(r_arcmin[i])+"'",marker='x')
    # plt.legend()
    # plt.plot(rad,np.mean(ratios_array,axis=0),label='Mean enclosed energy',marker='o')
    plt.title(BAND+' Enclosed energy for all points within 40'' FOV (estimated position)')
    plt.xlabel('Radius (um)')
    plt.ylabel('Percent enclosed energy (%)')
    plt.xlim((0,26))
    
    # means.append(np.mean(ratios_array,axis=0)) #this is what I am using to collect all of the means for later analysis
    #import the actual hexagon data
    def Hex_import():
        path = r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\Hexagon_OpticalPerf_data.csv"
        df = pandas.read_csv(path)
        hex_label = []
        hex_rad = []
        hex_frac = []
        for i in np.arange(len(df)):
            row = df.loc[i]
            band = row['Band']
            loc = row['Location']
            typ = row['Type']
            if band == BAND:
                if 'Hexagon '+band+' '+loc not in hex_label:    
                    hex_label.append('Hexagon '+band+' '+loc)
                if typ == 'Radius':
                    rad = row[3:]
                    hex_rad.append(rad)
                else:
                    frac = row[3:]
                    hex_frac.append(frac)
        return(hex_label,hex_rad,hex_frac)
    hex_label,hex_rad,hex_frac = Hex_import()
    
    for i in np.arange(len(hex_label)):
        plt.scatter(hex_rad[i],hex_frac[i],label=hex_label[i])
    plt.legend()
    
    print(np.min(fwhm))

    #%%
    '''
    making plots of the encircled energy by radius and FWHM by radius, a scatter plot of every measurement taken
    '''
    FOV_center = 500,500
    r = np.sqrt((x-FOV_center[0])**2+(y-FOV_center[1])**2)
    r_arcmin = r*4.9/60
    enc_2 = np.asarray(enc_2)
    fwhm = np.asarray(fwhm)
    
    plt.figure(figsize=(12,6))
    plt.subplot(121)
    plt.plot(r_arcmin,fwhm,'o')
    plt.xlabel('Radius from image center (arcmin)')
    plt.ylabel('FWHM (pix)')
    plt.title(BAND+' FWHM vs Field Position')
    plt.axvline(20,color='r',label='SPARCS FOV')
    plt.legend()
    
    plt.subplot(122)
    plt.plot(r_arcmin,enc_2,'o')
    plt.xlabel('Radius from image center (arcmin)')
    plt.ylabel('Enclosed Energy (%)')
    plt.title(BAND+' Enclosed energy in 2 pixels vs Field Position')
    plt.axvline(20,color='r',label='SPARCS FOV')
    plt.legend()
    
    fov = np.where(r_arcmin <= 20)[0]
    enc_fov = enc_2[fov]
    fwhm_fov = fwhm[fov]
    
    range_enc = np.ptp(enc_fov)
    range_fwhm = np.ptp(fwhm_fov)

 