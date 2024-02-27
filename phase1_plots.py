# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:06:20 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt


path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\FUV_photometry_Measurements_10.csv"
df = pandas.read_csv(path,delimiter=',')
#print(df)

x = df['X(FITS)_T1']
y = df['Y(FITS)_T1']
fwhm = df['Width_T1']
snr = df['Source_SNR_T1']

fig,ax=plt.subplots()
ax.set_xlim([0,1175])
ax.set_ylim([0,1033])
sc = plt.scatter(x,y,s=fwhm*50,c=snr)
plt.colorbar()
plt.title('FUV SNR by X,Y coordinate')
handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\NUV_photometry_Measurements_10.csv"
df = pandas.read_csv(path,delimiter=',')
#print(df)

x = df['X(FITS)_T1']
y = df['Y(FITS)_T1']
fwhm = df['Width_T1']
snr = df['Source_SNR_T1']

y[x<150] = np.nan
x[x<150] = np.nan

fig,ax=plt.subplots()
ax.set_xlim([0,1175])
ax.set_ylim([0,1033])
sc = plt.scatter(x,y,s=fwhm*50,c=snr)
plt.colorbar()
plt.title('NUV SNR by X,Y coordinate')
handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

#%% Let's see if we can do some ensquared energy plots
import astropy
from astropy.io import fits
from matplotlib.colors import LogNorm

i = 36
row = df.iloc[i]    
file = row['Label']
path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\FUV\\"+file
image_file = astropy.io.fits.open(path, cache=True)
image_data = fits.getdata(path)
# x,y=np.where(image_data == row['Peak_T1'])
# x=x[0]
# y=y[0]
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
    rad.append(i)
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
plt.plot(rad,percents)
plt.title('Percent enclosed energy vs pixel radius')
plt.xlabel('Radius (pix)')
plt.ylabel('Percent enclosed energy (%)')


#%%
ee_darksub_array = []
ratios_array = []
percents_array = []

for i in np.arange(len(df)):
    row = df.iloc[i]    
    file = row['Label']
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\FUV\\"+file
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
        rad.append(i)
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
    plt.plot(rad,percents)
    plt.title('Percent enclosed energy vs pixel radius')
    plt.xlabel('Radius (pix)')
    plt.ylabel('Percent enclosed energy (%)')
        
    ee_darksub_array.append(ee_darksub)
    ratios_array.append(ratios)
    percents_array.append(percents)

plt.figure()
enc_1 = []
for i in percents_array:
    enc_1.append(i[1])
plt.scatter(df['X(FITS)_T1'],df['Y(FITS)_T1'],c=enc_1)
    
limits = df['slice'][(df['X(FITS)_T1'] > 200) & (df['X(FITS)_T1'] < 800) & (df['Y(FITS)_T1'] > 200) & (df['Y(FITS)_T1'] < 800)]
temp = df.iloc[limits]
    
#radial field calculation
FUV_center = 430,550
x = temp['X(FITS)_T1']
y = temp['Y(FITS)_T1']
r = np.sqrt((x-FUV_center[0])**2+(y-FUV_center[1])**2)
r_arc = r/4.9
    
for i in limits:
    plt.plot(rad,percents_array[int(i)],label=int(r_arc[i]))
plt.legend() 
    
    
    
    
    















