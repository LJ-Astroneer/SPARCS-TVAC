# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:06:20 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt


path = r'C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/phase1_photosandimages/20240222/FUV_photometry_Measurements_10.csv'
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
plt.gca().invert_yaxis()
plt.title('FUV SNR by X,Y coordinate')
handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

path = r'C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/phase1_photosandimages/20240222/NUV_photometry_Measurements_10.csv'
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
plt.gca().invert_yaxis()
plt.title('NUV SNR by X,Y coordinate')
handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),np.median(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

#%%







