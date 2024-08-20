# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:49:57 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_calculated_photons.csv")
nuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\nuv_calculated_photons.csv")
photo = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\photodiode_data.csv")

fuv_ratios = []
fuv_wavelengths = []
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    incident = row['Adjusted Flux']
    inc_err = row['Adjusted Error']
    i = fuv['Wavelength (nm)']==int(wv)
    if len(fuv['Photons/s'][i]) > 0:
        meas = fuv['Photons/s'][i].values[0]
        meas_err = fuv['Error Estimate'][i].values[0]
        fuv_ratios.append(meas*100/incident)
        fuv_wavelengths.append(wv)

nuv_ratios = []
nuv_wavelengths = []
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    incident = row['Adjusted Flux']
    inc_err = row['Adjusted Error']
    i = nuv['Wavelength (nm)']==int(wv)
    if len(nuv['Photons/s'][i]) > 0:
        meas = nuv['Photons/s'][i].values[0]
        meas_err = nuv['Error Estimate'][i].values[0]
        nuv_ratios.append(meas*100/incident)
        nuv_wavelengths.append(wv)


plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')









