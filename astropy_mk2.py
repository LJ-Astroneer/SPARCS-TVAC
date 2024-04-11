# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 12:02:22 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.io import fits
from matplotlib.colors import LogNorm
from matplotlib import colors
from scipy import stats
from photutils.aperture import CircularAnnulus, CircularAperture
from photutils.background import Background2D
from astropy.stats import SigmaClip
from photutils.aperture import ApertureStats

folder = '20240222\FUV\dark_subtracted'
BAND = ['FUV']#,'NUV']
for BAND in BAND:
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    fwhm = df['Width_T1']
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    FOV_center = 500,500 #working assumption for now
    radius_center = (np.sqrt((x-FOV_center[0])**2+(y-FOV_center[1])**2))*4.9/60 #finding the radius from the center for all images in arcmin
    index = np.where(radius_center==min(radius_center))[0][0] #right now I just want to choose the center most image np.where(radius_center==min(radius_center))[0][0]
    
    for i in [index]: #np.arange(len(df))
        row = df.iloc[i]    #just collects all the info from that row
        file = row['Label'] #filename
        path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\\"+folder+"\\"+file
        image_file = astropy.io.fits.open(path, cache=True) #open fit
        image_data = fits.getdata(path) #get data
        image_data = image_data[:,:1065] #trim off the overscan
        x = int(row['X(FITS)_T1']) #all the X centroids 
        y = int(row['Y(FITS)_T1']) #all the Y centroids
        radial = radius_center[i]
        
        data = image_data
        positions = [x,y]
        radii = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5]
        apertures = [CircularAperture(positions, r=r) for r in radii]
        annulus_aperture = CircularAnnulus(positions, r_in=40, r_out=80)
        
        #code to find the mean value of the background in the annulus        
        from photutils.aperture import ApertureStats       
        aperstats = ApertureStats(data, annulus_aperture)
        bkg_mean = aperstats.mean
        #sigma clipped medians for the annulus
        sigclip = SigmaClip(sigma=3.0, maxiters=10)
        bkg_stats = ApertureStats(data, annulus_aperture, sigma_clip=sigclip)
        bkg_median = bkg_stats.median
        bkg_std = bkg_stats.std
        #print(bkg_mean)         
        
        #now do the photometry for the circular apertures
        from photutils.aperture import aperture_photometry
        phot_table = aperture_photometry(data, apertures)
        for col in phot_table.colnames:
            phot_table[col].info.format = '%.8g'  # for consistent table output
        #print(phot_table)
        
        aperture_area=[]
        total_bkg=[]
        sums=[]
        sums_bks=[]
        for ap in apertures:
            s = aperture_photometry(data,ap)['aperture_sum'][0]
            sums.append(s)
            area = ap.area_overlap(data)
            aperture_area.append(area)
            total_bkg.append(bkg_median * area)
         
        sums_bkg = [a_i - b_i for a_i, b_i in zip(sums, total_bkg)]
        ratios = [c_i/sums_bkg[-1] for c_i in sums_bkg]
        
        rad = [x*13 for x in radii]
        
        plt.figure(1) 
        plt.plot(rad,ratios,'-o',label=int(radial))
        plt.title(BAND+' Enclosed energy')
        plt.xlabel('Radius (um)')
        plt.ylabel('Fractional enclosed energy')
        plt.ylim((0,1.1))
        plt.legend()
        
        # bkg = annulus_aperture.to_mask().cutout(data)
        
        # #make a nice plot of background distribution for stats
        # plt.figure(2)
        # plt.hist(bkg,bins='auto') #Statistics, show a nice plot for the dark current
        # plt.title('Distributaiton of Background Pixels')
        # plt.xlabel('Pixel value')
        # plt.legend(['Median = {:.1f}, Std. Dev. = {:.1f}'.format(bkg_median,bkg_std)])
