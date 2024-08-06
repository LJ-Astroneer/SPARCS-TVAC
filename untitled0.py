# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 17:24:37 2024

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

means = []
stds = []
BAND = 'NUV'#,'NUV']
if BAND == 'FUV':
    folder = ['pre_focus','minus_0.01','plus_0.01','plus_0.015','plus_0.025','final']
else:
    folder = ['pre_focus','minus_0.01','plus_0.01','plus_0.015','plus_0.025','final','final2']
    
for folder in folder:
    # path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    path = "C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase1/phase1_photosandimages/20240319/"+folder+"/"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    fwhm = df['Width_T1']
    df = pandas.read_csv(path,delimiter=',')
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    snr = df['Source_SNR_T1']
    
    # if BAND == 'NUV':
    #     x=x.copy()
    #     y=y.copy()
    #     y[x<150] = np.nan
    #     x[x<150] = np.nan
    
    fig,ax=plt.subplots()
    ax.set_xlim([0,1065])
    ax.set_ylim([0,1033])
    sc = plt.scatter(x,y,s=fwhm*50,c=snr)
    plt.colorbar()
    plt.title(BAND+' SNR by X,Y coordinate')
    handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
    legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")
    
    ee_darksub_array = []
    ratios_array = []
    percents_array = []
    
    for i in np.arange(len(df)):
        row = df.iloc[i]    
        file = row['Label']
        path = "C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase1/phase1_photosandimages/20240319/"+folder+"/"+file
        image_file = astropy.io.fits.open(path, cache=True)
        image_data = fits.getdata(path)
        image_data = image_data[:,:1065]
        x = int(row['X(FITS)_T1'])
        y = int(row['Y(FITS)_T1'])
        mask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
        
        radii = np.arange(5,-1,-1)
        for i in radii:
            radius_ix = np.arange(x-i,x+i+1,1)
            radius_iy = np.arange(y-i,y+i+1,1)
            xv, yv = np.meshgrid(radius_ix,radius_iy)
            mask[yv,xv] = i+1
        
        num = []
        ee = []
        rad = []
        for i in radii:
            enc = np.where((mask > 0) & (mask <= i+1))
            num.append(len(enc[0]))
            ee.append(np.sum(image_data[enc]))
            rad.append((i+0.5)*13)
        num.reverse()
        rad.reverse()
        ee.reverse()
        
        darkmask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
        dradius = 30 #outer dark radius
        radius_ix = np.arange(x-dradius,x+dradius+1,1)
        radius_iy = np.arange(y-dradius,y+dradius+1,1)
        xv, yv = np.meshgrid(radius_ix,radius_iy)
        darkmask[yv,xv] = 1
        dradius_in = 20
        radius_ix = np.arange(x-dradius_in,x+dradius_in+1,1)
        radius_iy = np.arange(y-dradius_in,y+dradius_in+1,1)
        xv, yv = np.meshgrid(radius_ix,radius_iy)
        darkmask[yv,xv] = 0
        dark = np.mean(image_data[darkmask!=0])
        dark_error = np.std(image_data[darkmask!=0])
        
        total_dark = [i*dark for i in num]
        ee_darksub = [xi-yi for xi,yi in zip(ee,total_dark)]
        ratios = [i/ee_darksub[-1] for i in ee_darksub]
        percents = [i*100 for i in ratios]
        
        ratios.insert(0,0)
        percents.insert(0,0)
        rad.insert(0,0)
        
        ee_darksub_array.append(ee_darksub)
        ratios_array.append(ratios)
        percents_array.append(percents)
    
    plt.figure()
    enc_2 = []
    for i in percents_array:
        enc_2.append(i[1])
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2)
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+' Percent Enclosed energy in 1 pixels by field position')
    
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
            plt.plot(rad,ratios_array[int(i)],label='Radius = '+'{:.1f}'.format(r_arcmin[i])+"'",marker='x')
    # plt.legend()
    # plt.plot(rad,np.mean(ratios_array,axis=0),label='Mean enclosed energy',marker='o')
    plt.title(BAND+' Enclosed energy for all points within 40'' FOV (estimated position)')
    plt.xlabel('Radius (um)')
    plt.ylabel('Percent enclosed energy (%)')
    plt.xlim((0,20))
    
    means.append(np.mean(ratios_array,axis=0)) #this is what I am using to collect all of the means for later analysis
    stds.append(np.std(ratios_array,axis=0))

#%%
rad = [0,1,2,3,4,5,6]
if BAND == 'FUV':
    plt.figure()
    labels = ['Pre-focus, 0"','-0.01"','+0.01"','+0.015"','+0.025"','Final, +0.01"']
    for i in np.arange(len(means)):
        plt.errorbar(rad,means[i]*100,yerr=stds[i]*100,fmt=':o',capsize=3,label=labels[i])
    plt.title('FUV Enclosed energy with Focusing')
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Enclosed energy (%)')
    plt.xlim(0,5)
    plt.legend()
if BAND =='NUV':
    plt.figure()
    labels = ['Pre-focus, 0"','-0.01"','+0.01"','+0.015"','+0.025"','0"','Final, 0"']
    for i in np.arange(len(means)):
        plt.errorbar(rad,means[i]*100,yerr=stds[i]*100,fmt=':o',capsize=3,label=labels[i])
    plt.title('NUV Enclosed energy with Focusing')
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Enclosed energy (%)')
    plt.xlim(0,5)
    plt.legend()