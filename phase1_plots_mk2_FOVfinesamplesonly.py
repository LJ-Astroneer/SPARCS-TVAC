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
BAND = ['FUV']#,'NUV']
folder = '20240322/'+BAND[0]+'_FOV_fine'
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
    
    # fig,ax=plt.subplots()
    # ax.set_xlim([0,1065])
    # ax.set_ylim([0,1033])
    # sc = plt.scatter(x,y,s=fwhm*50,c=snr)
    # plt.colorbar()
    # plt.title(BAND+' SNR by X,Y coordinate')
    # handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
    # legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")
    
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
    '''

    from scipy.interpolate import griddata
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
    plt.xlim((0,26))
    
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
# labels = ['pre-focus FUV','pre-focus NUV','minus 0.01 FUV','minus 0.01 NUV','plus 0.01 FUV','plus 0.01 NUV','plus0.015 FUV','plus0.015 NUV','plus 0.025FUV','plus 0.025NUV','FUV final','NUV final','NUV final2']
# for i in [0,2,4,6,8,10]:
#     plt.plot(rad,means[i],marker='x',label=labels[i])
# plt.title('FUV Enclosed energy for Focus')
# plt.xlabel('Radius (um)')
# plt.ylabel('Ratio Enclosed energy')
# plt.xlim((0,20))
# plt.legend()

# plt.figure()
# for i in [1,3,5,7,9,11,12]:
#     plt.plot(rad,means[i],marker='x',label=labels[i])
# plt.title('NUV Enclosed energy for Focus')
# plt.xlabel('Radius (um)')
# plt.ylabel('Ratio Enclosed energy')
# plt.xlim((0,20))
# plt.legend()
    
#%% making plots of the encircled energy by radius and FWHM by radius
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

#%% What we need to do now is take the samples that were at each field location,
#and then take the average values with standard deviations to get error bars

fwhm_means=[]
fwhm_stds=[]
fwhm_meds=[]
fwhm_mads=[]
enc_means = []
enc_stds = []
enc_meds=[]
enc_mads=[]
xs = []
ys = []
rs = []
ratios_means = []
ratios_array=np.asarray(ratios_array)
i=0

if BAND == 'FUV':
    while i < len(x):
        if i == 15:
            index = [i]
            fwhm_means.append(np.mean(fwhm[index]))
            fwhm_stds.append(np.std(fwhm[index]))
            fwhm_meds.append(np.median(fwhm[index]))
            fwhm_mads.append(stats.median_abs_deviation(fwhm[index]))
            enc_means.append(np.mean(enc_2[index]))
            enc_stds.append(np.std(enc_2[index]))
            enc_meds.append(np.median(enc_2[index]))
            enc_mads.append(stats.median_abs_deviation(enc_2[index]))
            xs.append(np.mean(x[index]))
            ys.append(np.mean(y[index]))
            rs.append(np.mean(r[index]))
            ratios_means.append(np.mean(ratios_array[index],axis=0))
            print(i)
            i+=1
        if i == 16:
            index = np.arange(i,i+4)
            fwhm_means.append(np.mean(fwhm[index]))
            fwhm_stds.append(np.std(fwhm[index]))
            fwhm_meds.append(np.median(fwhm[index]))
            fwhm_mads.append(stats.median_abs_deviation(fwhm[index]))
            enc_means.append(np.mean(enc_2[index]))
            enc_stds.append(np.std(enc_2[index]))
            enc_meds.append(np.median(enc_2[index]))
            enc_mads.append(stats.median_abs_deviation(enc_2[index]))
            xs.append(np.mean(x[index]))
            ys.append(np.mean(y[index]))
            rs.append(np.mean(r[index]))
            ratios_means.append(np.mean(ratios_array[index],axis=0))
            print(index)
            i+=4
        if i == 215:
            index = np.arange(i,i+6)
            fwhm_means.append(np.mean(fwhm[index]))
            fwhm_stds.append(np.std(fwhm[index]))
            fwhm_meds.append(np.median(fwhm[index]))
            fwhm_mads.append(stats.median_abs_deviation(fwhm[index]))
            enc_means.append(np.mean(enc_2[index]))
            enc_stds.append(np.std(enc_2[index]))
            enc_meds.append(np.median(enc_2[index]))
            enc_mads.append(stats.median_abs_deviation(enc_2[index]))
            xs.append(np.mean(x[index]))
            ys.append(np.mean(y[index]))
            rs.append(np.mean(r[index]))
            ratios_means.append(np.mean(ratios_array[index],axis=0))
            print(index)
            i+=6
        else:
            index = np.arange(i,i+5)
            fwhm_means.append(np.mean(fwhm[index]))
            fwhm_stds.append(np.std(fwhm[index]))
            fwhm_meds.append(np.median(fwhm[index]))
            fwhm_mads.append(stats.median_abs_deviation(fwhm[index]))
            enc_means.append(np.mean(enc_2[index]))
            enc_stds.append(np.std(enc_2[index]))
            enc_meds.append(np.median(enc_2[index]))
            enc_mads.append(stats.median_abs_deviation(enc_2[index]))
            xs.append(np.mean(x[index]))
            ys.append(np.mean(y[index]))
            rs.append(np.mean(r[index]))
            ratios_means.append(np.mean(ratios_array[index],axis=0))
            print(index)
            i+=5
if BAND == 'NUV':
    while i < len(x):
        if i == 140:
            index = np.arange(i,i+4)
            fwhm_means.append(np.mean(fwhm[index]))
            fwhm_stds.append(np.std(fwhm[index]))
            fwhm_meds.append(np.median(fwhm[index]))
            fwhm_mads.append(stats.median_abs_deviation(fwhm[index]))
            enc_means.append(np.mean(enc_2[index]))
            enc_stds.append(np.std(enc_2[index]))
            enc_meds.append(np.median(enc_2[index]))
            enc_mads.append(stats.median_abs_deviation(enc_2[index]))
            xs.append(np.mean(x[index]))
            ys.append(np.mean(y[index]))
            rs.append(np.mean(r[index]))
            ratios_means.append(np.mean(ratios_array[index],axis=0))
            print(index)
            i+=4
        else:
            index = np.arange(i,i+5)
            fwhm_means.append(np.mean(fwhm[index]))
            fwhm_stds.append(np.std(fwhm[index]))
            fwhm_meds.append(np.median(fwhm[index]))
            fwhm_mads.append(stats.median_abs_deviation(fwhm[index]))
            enc_means.append(np.mean(enc_2[index]))
            enc_stds.append(np.std(enc_2[index]))
            enc_meds.append(np.median(enc_2[index]))
            enc_mads.append(stats.median_abs_deviation(enc_2[index]))
            xs.append(np.mean(x[index]))
            ys.append(np.mean(y[index]))
            rs.append(np.mean(r[index]))
            ratios_means.append(np.mean(ratios_array[index],axis=0))
            print(index)
            i+=5
fwhm_means=np.asarray(fwhm_means)
fwhm_stds=np.asarray(fwhm_stds)
fwhm_meds=np.asarray(fwhm_meds)
fwhm_mads=np.asarray(fwhm_mads)
enc_means =np.asarray(enc_means)
enc_stds =np.asarray(enc_stds)
enc_meds =np.asarray(enc_meds)
enc_mads =np.asarray(enc_mads)
xs =np.asarray(xs)
ys =np.asarray(ys)
rs =np.asarray(rs)
ratios_means=np.asarray(ratios_means)

plt.figure()        
plt.scatter(xs,ys,c=enc_means,s=300)
plt.colorbar()
plt.xlim((0,1175))
plt.ylim((0,1033))
plt.title(BAND+' Mean Enclosed energy % in 2 pixels by field position')
plt.xlabel('X Pixels')
plt.ylabel('Y Pixels')

plt.figure()
plt.scatter(xs,ys,c=fwhm_means,s=300,norm='linear',cmap='viridis_r')
plt.colorbar()
plt.xlim((0,1175))
plt.ylim((0,1033))
plt.title(BAND+' Mean FWHM by field position')
plt.xlabel('X Pixels')
plt.ylabel('Y Pixels')

rs_arcmin = rs*4.9/60
plt.figure(figsize=(12,6))
plt.subplot(121)
plt.plot(rs_arcmin,fwhm_means,'o')
plt.xlabel('Radius from image center (arcmin)')
plt.ylabel('FWHM (pix)')
plt.title(BAND+' Mean FWHM vs Field Position')
plt.axvline(20,color='r',label='SPARCS FOV')
plt.errorbar(rs_arcmin,fwhm_means,yerr=fwhm_stds,capsize=3,fmt='none')
plt.legend()

plt.subplot(122)
plt.plot(rs_arcmin,enc_means,'o')
plt.xlabel('Radius from image center (arcmin)')
plt.ylabel('Enclosed Energy (%)')
plt.title(BAND+' Mean Enclosed energy % in 2 pixels vs Field Position')
plt.axvline(20,color='r',label='SPARCS FOV')
plt.errorbar(rs_arcmin,enc_means,yerr=enc_stds,capsize=3,fmt='none')
plt.legend()

# plt.figure()        
# plt.scatter(xs,ys,c=enc_meds,s=300)
# plt.colorbar()
# plt.xlim((0,1175))
# plt.ylim((0,1033))
# plt.title(BAND+' Median Percent Enclosed energy in 2 pixels by field position')
# plt.xlabel('X Pixels')
# plt.ylabel('Y Pixels')

# plt.figure()
# plt.scatter(xs,ys,s=fwhm_meds*100,c=fwhm_meds,norm='linear',cmap='gist_rainbow')
# plt.colorbar()
# plt.xlim((0,1175))
# plt.ylim((0,1033))
# plt.title(BAND+' Median FWHM by field position')
# plt.xlabel('X Pixels')
# plt.ylabel('Y Pixels')

# rs_arcmin = rs*4.9/60
# plt.figure(figsize=(12,6))
# plt.subplot(121)
# plt.plot(rs_arcmin,fwhm_meds,'o')
# plt.xlabel('Radius from image center (arcmin)')
# plt.ylabel('FWHM (pix)')
# plt.title(BAND+' Median FWHM vs Field Position')
# plt.axvline(20,color='r',label='SPARCS FOV')
# plt.errorbar(rs_arcmin,fwhm_meds,yerr=fwhm_mads,capsize=3,fmt='none')
# plt.legend()

# plt.subplot(122)
# plt.plot(rs_arcmin,enc_meds,'o')
# plt.xlabel('Radius from image center (arcmin)')
# plt.ylabel('Enclosed Energy (%)')
# plt.title(BAND+' Median Enclosed energy in 2 pixels vs Field Position')
# plt.axvline(20,color='r',label='SPARCS FOV')
# plt.errorbar(rs_arcmin,enc_meds,yerr=enc_mads,capsize=3,fmt='none')
# plt.legend()


fov = np.where(rs_arcmin <= 20)[0]
enc_fov = enc_means[fov]
enc_stds_fov = enc_stds[fov]
fwhm_fov = fwhm_means[fov]
fwhm_stds_fov = fwhm_stds[fov]

def percent_change(x,x_err):
    n = max(x)-min(x)
    d = min(x)
    p = (n/d)*100
    e_max = x_err[np.where(x == max(x))[0]]
    e_min = x_err[np.where(x == min(x))[0]]
    sig_n = np.sqrt(e_max**2+e_min**2)
    sig_p = p*np.sqrt((sig_n/n)**2+(e_min/d)**2)
    return p,sig_p[0]

print(f'Enc max = {max(enc_fov):.1f}, min = {min(enc_fov):.1f}')
enc_p,enc_sig_p=percent_change(enc_fov,enc_stds_fov)
print(f'Enclosed energy change: {enc_p:.1f}% +/-{enc_sig_p:.1f}%')

print(f'FWHM max = {max(fwhm_fov):.1f}, min = {min(fwhm_fov):.1f}')
fwhm_p,fwhm_sig_p=percent_change(fwhm_fov,fwhm_stds_fov)
print(f'FWHM size change: {fwhm_p:.1f}% +/-{fwhm_sig_p:.1f}%')


#%% Mesh the averages
grid_x, grid_y = np.mgrid[:1033, :1175]
points = (np.array((ys,xs))).transpose() #flipped x and y here because I had to for it to work
values = np.array(fwhm_means)
grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')

plt.figure()
plt.subplot(221)
plt.scatter(xs,ys,c=fwhm_means,cmap='viridis_r')
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
plt.suptitle(BAND+' FWHM mean mesh interpolation')
plt.show()

values = np.array(enc_means)
grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')

plt.figure()
plt.subplot(221)
plt.scatter(xs,ys,c=enc_means)
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
plt.suptitle(BAND+' Encirncled Energy mean mesh interpolation')
plt.show()


   #%%

plt.figure() 
for i in np.arange(len(rs_arcmin)):
    if rs_arcmin[i] <= 20:
        plt.plot(rad,ratios_means[int(i)],label='Radius = '+'{:.1f}'.format(rs_arcmin[i])+"'",marker='x')
# plt.legend()
# plt.plot(rad,np.mean(ratios_array,axis=0),label='Mean enclosed energy',marker='o')
plt.title(BAND+' Enclosed energy for all points within 40'' FOV (estimated position)')
plt.xlabel('Radius (um)')
plt.ylabel('Percent enclosed energy (%)')
plt.xlim((0,26))

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
 
 