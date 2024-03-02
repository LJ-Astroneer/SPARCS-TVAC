# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:06:20 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.io import fits
from matplotlib.colors import LogNorm
#%% SNR plots and FWHM learning

# path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\FUV_photometry_Measurements_adaptive.csv"
# df = pandas.read_csv(path,delimiter=',')
# fwhm = df['Width_T1']
# path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\FUV_photometry_Measurements_10.csv"
# df = pandas.read_csv(path,delimiter=',')
# x = df['X(FITS)_T1']
# y = df['Y(FITS)_T1']
# snr = df['Source_SNR_T1']

# fig,ax=plt.subplots()
# ax.set_xlim([0,1175])
# ax.set_ylim([0,1033])
# sc = plt.scatter(x,y,s=fwhm*50,c=snr)
# plt.colorbar()
# plt.title('FUV SNR by X,Y coordinate')
# handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
# legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

# path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\NUV_photometry_Measurements_adaptive.csv"
# df = pandas.read_csv(path,delimiter=',')
# fwhm = df['Width_T1']
# path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\NUV_photometry_Measurements_10.csv"
# df = pandas.read_csv(path,delimiter=',')
# x = df['X(FITS)_T1']
# y = df['Y(FITS)_T1']
# snr = df['Source_SNR_T1']

# y[x<150] = np.nan
# x[x<150] = np.nan

# fig,ax=plt.subplots()
# ax.set_xlim([0,1175])
# ax.set_ylim([0,1033])
# sc = plt.scatter(x,y,s=fwhm*50,c=snr)
# plt.colorbar()
# plt.title('NUV SNR by X,Y coordinate')
# handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
# legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

#%% Let's see if we can do some ensquared energy plots This is the test case with only the best plot

# i = 36
# row = df.iloc[i]    
# file = row['Label']
# path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\NUV\\"+file
# image_file = astropy.io.fits.open(path, cache=True)
# image_data = fits.getdata(path)
# # x,y=np.where(image_data == row['Peak_T1'])
# # x=x[0]
# # y=y[0]
# x = int(row['X(FITS)_T1'])
# y = int(row['Y(FITS)_T1'])


# mask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)

# radii = np.arange(7,-1,-1)
# for i in radii:
#     radius_ix = np.arange(x-i,x+i+1,1)
#     radius_iy = np.arange(y-i,y+i+1,1)
#     xv, yv = np.meshgrid(radius_ix,radius_iy)
#     mask[yv,xv] = i+1

# num = []
# ee = []
# rad = []
# for i in radii:
#     enc = np.where((mask > 0) & (mask <= i+1))
#     num.append(len(enc[0]))
#     ee.append(np.sum(image_data[enc]))
#     rad.append(i)
# num.reverse()
# rad.reverse()
# ee.reverse()

# darkmask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
# dradius = 20
# radius_ix = np.arange(x-dradius,x+dradius+1,1)
# radius_iy = np.arange(y-dradius,y+dradius+1,1)
# xv, yv = np.meshgrid(radius_ix,radius_iy)
# darkmask[yv,xv] = 1
# darkmask[mask!=0] = 0
# dark = np.median(image_data[darkmask!=0])
# dark_error = np.std(image_data[darkmask!=0])

# total_dark = [i*dark for i in num]
# ee_darksub = [xi-yi for xi,yi in zip(ee,total_dark)]
# ratios = [i/ee_darksub[-1] for i in ee_darksub]
# percents = [i*100 for i in ratios]
# plt.plot(rad,percents)
# plt.title('Percent enclosed energy vs pixel radius')
# plt.xlabel('Radius (pix)')
# plt.ylabel('Percent enclosed energy (%)')



    
    
#%% Trying to make hexagon comparison images      
# ee_darksub_array = []
# ratios_array = []
# percents_array = []

# for i in np.arange(len(df)):
#     row = df.iloc[i]    
#     file = row['Label']
#     path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\\"+file
#     image_file = astropy.io.fits.open(path, cache=True)
#     image_data = fits.getdata(path)
#     x = int(row['X(FITS)_T1'])
#     y = int(row['Y(FITS)_T1'])
#     mask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
    
#     radii = np.arange(7,-1,-1)
#     for i in radii:
#         radius_ix = np.arange(x-i,x+i+1,1)
#         radius_iy = np.arange(y-i,y+i+1,1)
#         xv, yv = np.meshgrid(radius_ix,radius_iy)
#         mask[yv,xv] = i+1
    
#     num = []
#     ee = []
#     rad = []
#     for i in radii:
#         enc = np.where((mask > 0) & (mask <= i+1))
#         num.append(len(enc[0]))
#         ee.append(np.sum(image_data[enc]))
#         rad.append((i+0.5)*13)
#     num.reverse()
#     rad.reverse()
#     ee.reverse()
    
#     darkmask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
#     dradius = 20
#     radius_ix = np.arange(x-dradius,x+dradius+1,1)
#     radius_iy = np.arange(y-dradius,y+dradius+1,1)
#     xv, yv = np.meshgrid(radius_ix,radius_iy)
#     darkmask[yv,xv] = 1
#     darkmask[mask!=0] = 0
#     dark = np.median(image_data[darkmask!=0])
#     dark_error = np.std(image_data[darkmask!=0])
    
#     total_dark = [i*dark for i in num]
#     ee_darksub = [xi-yi for xi,yi in zip(ee,total_dark)]
#     ratios = [i/ee_darksub[-1] for i in ee_darksub]
#     percents = [i*100 for i in ratios]
    
#     ratios.insert(0,0)
#     percents.insert(0,0)
#     rad.insert(0,0)
    
#     ee_darksub_array.append(ee_darksub)
#     ratios_array.append(ratios)
#     percents_array.append(percents)

# plt.figure()
# enc_2 = []
# for i in percents_array:
#     enc_2.append(i[1])
# plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2)
# plt.colorbar()
# plt.xlim((0,1175))
# plt.ylim((0,1033))
# plt.title('Percent Enclosed energy in 1 pixels by field position')

# #radial field calculation
# FUV_center = 430,550
# NUV_center = 500,550
# x = df['X(FITS)_T1']
# y = df['Y(FITS)_T1']
# r = np.sqrt((x-FUV_center[0])**2+(y-FUV_center[1])**2)
# r_arcmin = r*4.9/60
# plt.figure() 
# for i in np.arange(len(r_arcmin)):
#     if r_arcmin[i] <= 20:
#         plt.plot(rad,ratios_array[int(i)],label='Radius = '+'{:.1f}'.format(r_arcmin[i])+"'",marker='x')
# # plt.legend() 
# plt.title('Enclosed energy for all points within 40" FOV (estimated position)')
# plt.xlabel('Radius (um)')
# plt.ylabel('Percent enclosed energy (%)')
# plt.xlim((0,20))

# #import the actual hexagon data
# def Hex_import():
#     path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\Hexagon_OpticalPerf_data.csv"
#     df = pandas.read_csv(path)
#     hex_label = []
#     hex_rad = []
#     hex_frac = []
#     for i in np.arange(len(df)):
#         row = df.loc[i]
#         band = row['Band']
#         loc = row['Location']
#         typ = row['Type']
#         if 'Hexagon '+band+' '+loc not in hex_label:    
#             hex_label.append('Hexagon '+band+' '+loc)
#         if typ == 'Radius':
#             rad = row[3:]
#             hex_rad.append(rad)
#         else:
#             frac = row[3:]
#             hex_frac.append(frac)
#     return(hex_label,hex_rad,hex_frac)
# hex_label,hex_rad,hex_frac = Hex_import()

# for i in np.arange(len(hex_label)):
#     plt.scatter(hex_rad[i],hex_frac[i],label=hex_label[i])
# plt.legend()
#%% Make it all happen in 1 click
'''
Requirements to Run: 
    -Photometry results from astroimageJ with name BAND_photometry_Measurements_*.csv
        You can change the * to whatever but then you will need to change it in this file
        There are 2 files below because adaptive aperture gave a better fwhm, if you do not want 2 seperate files, delete the second import
    -a folder where that photometry file and all of your desired image files are saved
    -the hexagon csv saved where it is
'''
folder = input("What folder you want?! (20240222,) \n")
BAND = ['FUV','NUV']
for BAND in BAND:
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    fwhm = df['Width_T1']
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_10.csv"
    df = pandas.read_csv(path,delimiter=',')
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    snr = df['Source_SNR_T1']
    
    if BAND == 'NUV':
        x=x.copy()
        y=y.copy()
        y[x<150] = np.nan
        x[x<150] = np.nan
    
    fig,ax=plt.subplots()
    ax.set_xlim([0,1175])
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
        path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\\"+file
        image_file = astropy.io.fits.open(path, cache=True)
        image_data = fits.getdata(path)
        x = int(row['X(FITS)_T1'])
        y = int(row['Y(FITS)_T1'])
        mask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
        
        radii = np.arange(7,-1,-1)
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
        dradius = 20
        radius_ix = np.arange(x-dradius,x+dradius+1,1)
        radius_iy = np.arange(y-dradius,y+dradius+1,1)
        xv, yv = np.meshgrid(radius_ix,radius_iy)
        darkmask[yv,xv] = 1
        darkmask[mask!=0] = 0
        dark = np.median(image_data[darkmask!=0])
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
        FOV_center = 430,550
    elif BAND == 'NUV':
        FOV_center = 500,550
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    r = np.sqrt((x-FOV_center[0])**2+(y-FOV_center[1])**2)
    r_arcmin = r*4.9/60
    plt.figure() 
    for i in np.arange(len(r_arcmin)):
        if r_arcmin[i] <= 20:
            plt.plot(rad,ratios_array[int(i)],label='Radius = '+'{:.1f}'.format(r_arcmin[i])+"'",marker='x')
    # plt.legend() 
    plt.title(BAND+' Enclosed energy for all points within 40" FOV (estimated position)')
    plt.xlabel('Radius (um)')
    plt.ylabel('Percent enclosed energy (%)')
    plt.xlim((0,20))
    
    #import the actual hexagon data
    def Hex_import():
        path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\Hexagon_OpticalPerf_data.csv"
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