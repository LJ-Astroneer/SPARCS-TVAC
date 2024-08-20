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

plt.figure()
plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Throughput (%)')
plt.title('Throughput vs Wavelength')




fuv_ratios = []
fuv_wavelengths = []
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    incident = row['Normalized Response (Flux/Median)']
    inc_err = row['Adjusted Error']
    i = fuv['Wavelength (nm)']==int(wv)
    if len(fuv['Electrons/s'][i]) > 0:
        meas = fuv['Electrons/s'][i].values[0]
        meas_err = fuv['Error Estimate'][i].values[0]
        fuv_ratios.append(meas/incident)
        fuv_wavelengths.append(wv)

nuv_ratios = []
nuv_wavelengths = []
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    incident = row['Normalized Response (Flux/Median)']
    inc_err = row['Adjusted Error']
    i = nuv['Wavelength (nm)']==int(wv)
    if len(nuv['Electrons/s'][i]) > 0:
        meas = nuv['Electrons/s'][i].values[0]
        meas_err = nuv['Error Estimate'][i].values[0]
        nuv_ratios.append(meas/incident)
        nuv_wavelengths.append(wv)

plt.figure()
plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Electrons/second')
plt.title('Payload Response: Electron Flux / normalized photodiode data')


import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
def gaussian(x, amp, cen, width, offset):
    return amp * np.exp(-(x-cen)**2 / (2*width**2)) + offset
# Initial guess for the parameters
initial_guess = [1e6, 160, 60, 1e3]  # [amplitude, center, width, offset]

# Example data generation
x = nuv_wavelengths
y = nuv_ratios

# Fit the curve
popt, pcov = curve_fit(gaussian, x, y, p0=initial_guess)

# Extract the fitted parameters
amp, cen, width, offset = popt

# Calculate FWHM
fwhm = 2.355 * width

# Median x value (center of the Gaussian)
median_x = cen

# Print results
print(f"Fitted parameters: Amplitude = {amp:.2f}, Center = {cen:.2f}, Width = {width:.2f}, Offset = {offset:.2f}")
print(f"FWHM: {fwhm:.2f}")
print(f"Median x value of the Gaussian: {median_x:.2f}")


plt.figure()
plt.scatter(x, y, label='Data')
plt.plot(x, gaussian(x, *popt), label='Fitted Gaussian', color='red')
plt.legend()
plt.show()






