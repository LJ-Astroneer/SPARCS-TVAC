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
from matplotlib import colors
from scipy import stats
means = []
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
#%% Single file version

folder = '20240222\FUV\dark_subtracted'
BAND = ['FUV']#,'NUV']
for BAND in BAND:
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    fwhm = df['Width_T1']
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    snr = df['Source_SNR_T1']
    FOV_center = 500,500 #working assumption for now
    r = np.sqrt((x-FOV_center[0])**2+(y-FOV_center[1])**2) #finding the radius from the center for all images
    index = np.where(r==min(r))[0][0] #np.where(r<=20*4.9)[0]#np.where(r==min(r))[0][0] #right now I just want to choose the center most image
    
    #make some lists to fill
    ee_darksub_array = []
    ratios_array = []
    percents_array = []
    for i in [index]:
        row = df.iloc[i]    #just collects all the info from that row
        file = row['Label'] #filename
        path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+file
        image_file = astropy.io.fits.open(path, cache=True) #open fit
        image_data = fits.getdata(path) #get data
        image_data = image_data[:,:1065] #trim off the overscan
        x = 500#int(row['X(FITS)_T1']) #all the X centroids 
        y = 800#int(row['Y(FITS)_T1']) #all the Y centroids
        
        mask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16) #this will be an array that is used for selecting areas of an image
        radii = np.arange(5,-1,-1) #the radii to cover, list is reversed because you want to start with the largest and go to the smallest because each mask is on 'top' of the previous
        for i in radii:
            radius_ix = np.arange(x-i,x+i+1,1) #x values centered on the centroid X
            radius_iy = np.arange(y-i,y+i+1,1) #y values centered on the centroid Y
            xv, yv = np.meshgrid(radius_ix,radius_iy) #makes a grid to fill in all the x and y values between the bounds
            mask[yv,xv] = i+1 #each layer has a value to assist in identifying the masks later. 
            
        num = []
        ee = []
        rad = []
        src_std = []
        for i in radii:
            enc = np.where((mask > 0) & (mask <= i+1)) #mask=0 for unused pixels, and you want everything inside a radius
            num.append(len(enc[0])) #count the pixels in each radius, will need for dark subtraction later
            ee.append(np.sum(image_data[enc])) #actually sum up the energy enclosed
            rad.append((i+0.5)*13) #convert the radius to microns for SPARCS 13um per pixel, the center pixel has a radius of 0.5
            std = 1.48*np.median(np.abs(image_data[enc]-np.median(image_data[enc]))) #robust standard deviation calculation from Nat Butler
            src_std.append(std)
        #flip these all because right now they are outside in and we want to plot from the middle out
        num.reverse()
        rad.reverse()
        ee.reverse()
        src_std.reverse()
        
        #now make another mask for the background/dark annulus
        darkmask = np.empty((len(image_data), len(image_data[0])), dtype=np.uint16)
        dradius = 80 #outer annulus radius
        radius_ix = np.arange(x-dradius,x+dradius+1,1)
        radius_iy = np.arange(y-dradius,y+dradius+1,1)
        xv, yv = np.meshgrid(radius_ix,radius_iy)
        darkmask[yv,xv] = 1 #sets everything inside of outer pix radius to 1
        dradius_in = 40 #inner annulus radius
        radius_ix = np.arange(x-dradius_in,x+dradius_in+1,1)
        radius_iy = np.arange(y-dradius_in,y+dradius_in+1,1)
        xv, yv = np.meshgrid(radius_ix,radius_iy)
        darkmask[yv,xv] = 0 #sets inside of inner pix radius to 0
        #everything that is NOT 0 in darkmask is being used for the dark counting
        
        #make an image of the mask just to have for reference if you want it
        plt.figure(3)
        tempmask = mask+darkmask*-1
        plt.imshow(tempmask)
        plt.title('Masking for Encircled Energy')
        
        
        
        
        dark = image_data[darkmask!=0] #take all the image pixels in that annulus
        dark_median = np.median(dark) #median  of the dark
        dark_mean = np.mean(dark)
        dark_mode = stats.mode(dark)[0]
        dark_std = np.std(dark) #std of the dark for sigma clipping
        #to be extra fancy we are going to implement a 3sigma cutoff a la Howell to improve the stats
        dark_cutoff = dark[(dark > dark_median-3*dark_std) & (dark < dark_median+3*dark_std)]
        cutoff_num = len(dark) - len(dark_cutoff) #just to have as a reference of how many pixels fell outside of this range
        dark_median = np.median(dark_cutoff) #median of the dark
        dark_mean = np.mean(dark_cutoff)
        dark_pix = dark_mean
        dark_std = 1.48*np.median(np.abs(dark-np.median(dark)))
        
        
        #make a nice plot of background distribution for stats
        plt.figure(2)
        plt.hist(dark_cutoff,bins='auto') #Statistics, show a nice plot for the dark current
        plt.title('Distributaiton of Background Pixels')
        plt.xlabel('Pixel value')
        plt.legend(['Mean = {:.1f}, Std. Dev. = {:.1f}'.format(dark_median,dark_std)])
        
        total_dark = [i*dark_pix for i in num] #simply mulitply the backround by the number of pixels in each source radius
        ee_darksub = [xi-yi for xi,yi in zip(ee,total_dark)] #subtract the total dark from the encircled energies
        ratios = [i/ee_darksub[-1] for i in ee_darksub] #the ratio of each radii's energy to the largest radii's energy
        percents = [i*100 for i in ratios] #convert to percent if you want it
        
        ##Calculate the errorbar

        sig_ee_darksub = [np.sqrt(i**2+dark_std**2) for i in src_std] 
        sig_x = [ratios[i]*np.sqrt((sig_ee_darksub[i]/ee_darksub[i])**2+(sig_ee_darksub[-1]/ee_darksub[-1])**2) for i in np.arange(len(ratios))]
        
        radii = radii.tolist()
        radii.reverse()
        radii = [a+0.5 for a in radii]
        
        
        #these only matter when doing muplitple files
        ee_darksub_array.append(ee_darksub)
        ratios_array.append(ratios)
        percents_array.append(percents)
        #radial field calculation, here I select all the results that

        plt.figure(1) 
        plt.plot(radii,ratios,'-o')
        plt.title(BAND+' Enclosed energy')
        plt.xlabel('Radius (um)')
        plt.ylabel('Fractional enclosed energy')
        #plt.ylim((0,1.1))



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
folder = input("What folder you want?! (20240222,20240318/final_today,20240321) \n")
BAND = ['NUV']#,'NUV']
for BAND in BAND:
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    fwhm = df['Width_T1']
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
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
        path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\\"+folder+"\\"+file
        image_file = astropy.io.fits.open(path, cache=True)
        image_data = fits.getdata(path)
        image_data = image_data[:,:1065]
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
        enc_2.append(i[2])
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2)
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+' Percent Enclosed energy in 2 pixels by field position')
    
    plt.figure()
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],s=fwhm*100,c=fwhm,norm='linear',cmap='gist_rainbow')
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+' FWHM by field position')
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
    '''

    from scipy.interpolate import griddata
    grid_x, grid_y = np.mgrid[:1033, :1175]
    points = (np.array((df['Y(FITS)_T1'],df['X(FITS)_T1']))).transpose() #flipped x and y here because I had to for it to work
    values = np.array(enc_2)
    grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')
    
    plt.subplot(221)
    plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_2)
    plt.colorbar()
    plt.xlim((0,1175))
    plt.ylim((0,1033))
    plt.title(BAND+'Data Acquired')
    plt.subplot(222)
    plt.imshow(grid_z0,origin='lower')
    plt.colorbar()
    plt.title('nearest')
    plt.subplot(223)
    plt.imshow(grid_z1,origin='lower')
    plt.colorbar()
    plt.title('Linear')
    plt.subplot(224)
    plt.imshow(grid_z2,origin='lower')
    plt.colorbar()
    plt.title('Cubic')
    plt.show()
    
    
    #%%
    
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
    
    # means.append(np.mean(ratios_array,axis=0)) #this is what I am using to collect all of the means for later analysis
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
    
    print(np.min(fwhm))
#%%
labels = ['pre-focus FUV','pre-focus NUV','minus 0.01 FUV','minus 0.01 NUV','plus 0.01 FUV','plus 0.01 NUV','plus0.015 FUV','plus0.015 NUV','plus 0.025FUV','plus 0.025NUV','FUV final','NUV final','NUV final2']
for i in [0,2,4,6,8,10]:
    plt.plot(rad,means[i],marker='x',label=labels[i])
plt.title('FUV Enclosed energy for Focus')
plt.xlabel('Radius (um)')
plt.ylabel('Ratio Enclosed energy')
plt.xlim((0,20))
plt.legend()

plt.figure()
for i in [1,3,5,7,9,11,12]:
    plt.plot(rad,means[i],marker='x',label=labels[i])
plt.title('NUV Enclosed energy for Focus')
plt.xlabel('Radius (um)')
plt.ylabel('Ratio Enclosed energy')
plt.xlim((0,20))
plt.legend()
    
    
    