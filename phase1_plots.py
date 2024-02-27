# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:06:20 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt


path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\FUV_photometry_Measurements.xls"
df = pandas.read_csv(path,delimiter='\t')
#print(df)

x = df['X(FITS)_T1']
y = df['Y(FITS)_T1']
fwhm = df['Width_T1']
snr = df['Source_SNR_T1']

fig,ax=plt.subplots()
sc = plt.scatter(x,y,s=fwhm*50,c=snr)
plt.colorbar()
plt.gca().invert_yaxis()
plt.title('FUV SNR by X,Y coordinate')
handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm),max(fwhm)],func = lambda x: x/50,alpha=0.6)
legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")

path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\20240222\NUV_photometry_Measurements.xls"
df = pandas.read_csv(path,delimiter='\t')
#print(df)

x = df['X(FITS)_T1']
y = df['Y(FITS)_T1']
fwhm = df['Width_T1']
snr = df['Source_SNR_T1']

fig,ax=plt.subplots()
sc = plt.scatter(x,y,s=fwhm*50,c=snr)
plt.colorbar()
plt.gca().invert_yaxis()
plt.title('NUV SNR by X,Y coordinate')
handles, labels = sc.legend_elements(prop="sizes",num=[min(fwhm[fwhm!=0]),max(fwhm)],func = lambda x: x/50,alpha=0.6)
legend2 = ax.legend(handles, labels, loc="upper right", title="FWHM (pix)")