# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 12:07:53 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuvALL3_MEDIAN_COMBINE.csv")

target = fuv['Source-Sky_T1']*4.2/fuv['EXPTIME']
ghost1 = fuv['Source-Sky_C2']*4.2/fuv['EXPTIME']
ghost2 = fuv['Source-Sky_C3']*4.2/fuv['EXPTIME']

target_err = fuv['Source_Error_T1']*4.2/fuv['EXPTIME']
ghost1_err = fuv['Source_Error_C2']*4.2/fuv['EXPTIME']
ghost2_err = fuv['Source_Error_C3']*4.2/fuv['EXPTIME']

wv = fuv['Wavelength (nm)']

plt.figure()
plt.scatter(wv,target,label='Target')
plt.scatter(wv,ghost1,label='Ghost1')
plt.scatter(wv,ghost2,label='Ghost2')
plt.legend()
plt.yscale('log')
plt.title('Intensity versus wavelength')
plt.ylabel('Electrons / Second measured')
plt.xlabel('Wavelength (nm)')


#%%
fuv_qe = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\QE from JPL\fuv_QE.csv")

#QE is n_e/n_photons so n_e/QE = n_photons
target_photons=[]
target_photons_err=[]
fuv_combined_statistics=[]
ghost1_photons=[]
ghost1_photons_err=[]
ghost2_photons=[]
ghost2_photons_err=[]

for index,row in fuv.iterrows():
    wv = int(row['Wavelength (nm)'])
    target = row['Source-Sky_T1']*4.2/row['EXPTIME']
    ghost1 = row['Source-Sky_C2']*4.2/row['EXPTIME']
    ghost2 = row['Source-Sky_C3']*4.2/row['EXPTIME']
    target_err = row['Source_Error_T1']*4.2/row['EXPTIME']
    ghost1_err = row['Source_Error_C2']*4.2/row['EXPTIME']
    ghost2_err = row['Source_Error_C3']*4.2/row['EXPTIME']
    
    i = fuv_qe['wav[nm]']==int(wv)
    qe = fuv_qe['ave QE [%]'][i].values[0]
    target_photons = (target/qe)
    target_photons_err=(target_err/qe)
    ghost1_photons=(ghost1/qe)
    ghost1_photons_err=(ghost1_err/qe)
    ghost2_photons=(ghost2/qe)
    ghost2_photons_err=(ghost2_err/qe)
    stats = {
        'Wavelength (nm)': wv,
        'Target Electrons/s': target,
        'Target Electron Error':target_err,
        'Ghost1 Electrons/s': ghost1,
        'Ghost1 Electron Error':ghost1_err,
        'Ghost2 Electrons/s': ghost2,
        'Ghost2 Electron Error':ghost2_err,
        'QE': qe,
        'Target Photons/s': target_photons,
        'Target Photon Error Estimate': target_photons_err,
        'Ghost1 Photons/s': ghost1_photons,
        'Ghost1 Photon Error Estimate': ghost1_photons_err,
        'Ghost2 Photons/s': ghost2_photons,
        'Ghost2 Photon Error Estimate': ghost2_photons_err,
    }
    fuv_combined_statistics.append(stats)
output_csv =r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_ghosts_calculated_photons.csv"
with open(output_csv, mode='w', newline='') as csvfile:
    fieldnames = ['Wavelength (nm)', 'Target Electrons/s','Target Electron Error','Ghost1 Electrons/s','Ghost1 Electron Error','Ghost2 Electrons/s','Ghost2 Electron Error','QE', 'Target Photons/s','Target Photon Error Estimate','Ghost1 Photons/s','Ghost1 Photon Error Estimate','Ghost2 Photons/s','Ghost2 Photon Error Estimate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for stat in fuv_combined_statistics:
        writer.writerow(stat)
print(f"Combined statistics saved to {output_csv}")













































