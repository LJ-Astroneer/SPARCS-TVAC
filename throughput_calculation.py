# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:49:57 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.optimize import curve_fit

fuv = pd.read_csv(r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_calculated_photons.csv")
nuv = pd.read_csv(r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\nuv_calculated_photons.csv")
photo = pd.read_csv(r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\photodiode_data.csv")


#%% Make plots of the signal photons divided by the incident photons
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


#%%
def gaussian(x, amp, cen, width, offset):
    return amp * np.exp(-(x-cen)**2 / (2*width**2)) + offset
# Initial guess for the parameters
initial_guess = [20, 160, 60, 1e3]  # [amplitude, center, width, offset]

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


#%%Make plots divided by the normalized response instead

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


#%%
def gaussian(x, amp, cen, width, offset):
    return amp * np.exp(-(x-cen)**2 / (2*width**2)) + offset
# Initial guess for the parameters
initial_guess = [1e6, 160, 60, 1e3]  # [amplitude, center, width, offset]
# Example data generation
x = fuv_wavelengths
y = fuv_ratios
# Fit the curve
popt, pcov = curve_fit(gaussian, x, y, p0=initial_guess)
# Extract the fitted parameters
amp, cen, width, offset = popt
# Calculate FWHM
fwhm = 2.355 * width
# Median x value (center of the Gaussian)
median_x = cen
# Print results
print(f"FUV Fitted parameters: Amplitude = {amp:.2f}, Center = {cen:.2f}, Width = {width:.2f}, Offset = {offset:.2f}")
print(f"FUV FWHM: {fwhm:.2f}")
print(f"FUV Median x value of the Gaussian: {median_x:.2f}")
plt.figure()
plt.scatter(x, y, label='FUV Data')
plt.plot(x, gaussian(x, *popt), label='FUV Fitted Gaussian', color='red')
plt.legend()
plt.show()

# Initial guess for the parameters
initial_guess = [2e6, 280, 60, 1e3]  # [amplitude, center, width, offset]
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
print(f"NUV Fitted parameters: Amplitude = {amp:.2f}, Center = {cen:.2f}, Width = {width:.2f}, Offset = {offset:.2f}")
print(f"NUV FWHM: {fwhm:.2f}")
print(f"NUV Median x value of the Gaussian: {median_x:.2f}")
plt.scatter(x, y, label='NUV Data')
plt.plot(x, gaussian(x, *popt), label='NUV Fitted Gaussian')
plt.legend()
plt.show()




#%% Testing out my own interpolation
# test = pd.read_csv(r'D:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/Throughput/QE from JPL/jpl_fuvqe_loganinterp.csv')
# fuv_ratios = []
# fuv_wavelengths = []
# for index,row in photo.iterrows():
#     wv = round(row['Wavelength [nm]'])
#     incident = row['Adjusted Flux']
#     inc_err = row['Adjusted Error']
#     i = fuv['Wavelength (nm)']==int(wv)
#     if len(fuv['Electrons/s'][i]) > 0:
#         meas = fuv['Electrons/s'][i].values[0]
#         meas_err = fuv['Error Estimate'][i].values[0]
#         qe = test['QE'][test['wavelength']==wv].values[0]
#         fuv_ratios.append((meas/qe)*100/incident)
#         fuv_wavelengths.append(wv)

# nuv_ratios = []
# nuv_wavelengths = []
# for index,row in photo.iterrows():
#     wv = round(row['Wavelength [nm]'])
#     incident = row['Adjusted Flux']
#     inc_err = row['Adjusted Error']
#     i = nuv['Wavelength (nm)']==int(wv)
#     if len(nuv['Electrons/s'][i]) > 0:
#         meas = nuv['Electrons/s'][i].values[0]
#         meas_err = nuv['Error Estimate'][i].values[0]
#         nuv_ratios.append(meas*100/incident)
#         nuv_wavelengths.append(wv)

# plt.figure()
# plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
# plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')
# plt.xlabel('Wavelength (nm)')
# plt.ylabel('Throughput (%)')
# plt.title('Throughput vs Wavelength')
