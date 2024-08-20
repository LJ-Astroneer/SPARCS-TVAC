# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 12:07:53 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_combined_throughput_median.csv")
nuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\nuv_combined_throughput_median.csv")

fuv_err = fuv['Source_Error_T1']*4.2/fuv['EXPTIME']
nuv_err = nuv['Source_Error_T1']*4.5/nuv['EXPTIME']

plt.errorbar(fuv['Wavelength (nm)'],fuv['(Source-sky)*Gain/EXP'],fuv_err,8/2.355,fmt='-o',capsize=4) #the bandpass is 8nm FWHM so to std dev is FWHM/2.355
plt.errorbar(nuv['Wavelength (nm)'],nuv['(Source-sky)*Gain/EXP'],nuv_err,8/2.355,fmt='-o',capsize=4) #the bandpass is 8nm FWHM so to std dev is FWHM/2.355
plt.yscale('log')
plt.title('Measured intensity vs Wavelength')
plt.ylabel('Intensity (e-/s)')
plt.xlabel('Wavelength (nm)')

fuv_qe = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\QE from JPL\fuv_QE.csv")
nuv_qe = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\QE from JPL\nuv_QE.csv")

#QE is n_e/n_photons so n_e/QE = n_photons
fuv_photons=[]
fuv_photons_err=[]
fuv_combined_statistics=[]
for index,row in fuv.iterrows():
    wv = int(row['Wavelength (nm)'])
    electrons = row['(Source-sky)*Gain/EXP']
    i = fuv_qe['wav[nm]']==int(wv)
    qe = fuv_qe['avg QE'][i].values[0]
    fuv_photons.append(electrons/qe)
    fuv_photons_err.append((row['Source_Error_T1']*4.2/row['EXPTIME'])/qe)
    # Store the results
    stats = {
        'Wavelength (nm)': wv,
        'Electrons/s': electrons,
        'QE': qe,
        'Photons/s': electrons/qe,
        'Error Estimate': (row['Source_Error_T1']*4.2/row['EXPTIME'])/qe,
    }
    fuv_combined_statistics.append(stats)
output_csv =r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_calculated_photons.csv"
with open(output_csv, mode='w', newline='') as csvfile:
    fieldnames = ['Wavelength (nm)', 'Electrons/s','QE', 'Photons/s','Error Estimate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for stat in fuv_combined_statistics:
        writer.writerow(stat)

print(f"Combined statistics saved to {output_csv}")


    
nuv_photons=[]
nuv_photons_err=[]
nuv_combined_statistics=[]
for index,row in nuv.iterrows():
    wv = int(row['Wavelength (nm)'])
    electrons = row['(Source-sky)*Gain/EXP']
    i = nuv_qe['wavelength [nm]']==int(wv)
    qe = nuv_qe['Avg QE'][i].values[0]
    nuv_photons.append(electrons/qe)
    nuv_photons_err.append((row['Source_Error_T1']*4.5/row['EXPTIME'])/qe)
    stats = {
        'Wavelength (nm)': wv,
        'Electrons/s': electrons,
        'QE': qe,
        'Photons/s': electrons/qe,
        'Error Estimate': (row['Source_Error_T1']*4.5/row['EXPTIME'])/qe,
    }
    nuv_combined_statistics.append(stats)
output_csv =r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\nuv_calculated_photons.csv"
with open(output_csv, mode='w', newline='') as csvfile:
    fieldnames = ['Wavelength (nm)', 'Electrons/s','QE', 'Photons/s','Error Estimate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for stat in nuv_combined_statistics:
        writer.writerow(stat)

print(f"Combined statistics saved to {output_csv}")


plt.figure()    
plt.errorbar(fuv['Wavelength (nm)'],fuv_photons,fuv_photons_err,8/2.355,fmt='-o',capsize=4) #the bandpass is 8nm FWHM so to std dev is FWHM/2.355
plt.errorbar(nuv['Wavelength (nm)'],nuv_photons,nuv_photons_err,8/2.355,fmt='-o',capsize=4) #the bandpass is 8nm FWHM so to std dev is FWHM/2.355
plt.yscale('log')
plt.title('Measured intensity vs Wavelength')
plt.ylabel('Intensity (photons/s)')
plt.xlabel('Wavelength (nm)')