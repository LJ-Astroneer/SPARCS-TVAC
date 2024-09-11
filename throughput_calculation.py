# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:49:57 2024

@author: logan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

fuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\fuv_calculated_photons.csv")
nuv = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\nuv_calculated_photons.csv")
photo = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\photodiode_data.csv")
fuv_qe = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\QE from JPL\SPARCS_FUV_QE_2023.08.31.csv")
nuv_qe = pd.read_csv(r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\QE from JPL\SPARCS_NUV_QE_2023.10.24_ALL.csv")

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
        meas_err = fuv['Photon Error Estimate'][i].values[0]
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
        meas_err = nuv['Photon Error Estimate'][i].values[0]
        nuv_ratios.append(meas*100/incident)
        nuv_wavelengths.append(wv)

plt.figure()
plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Throughput (%)')
plt.title('Throughput vs Wavelength')
'''
note here that I never handled the error bars well and also the QE error from JPL
was not accounted for at all so this may be invalid anyway
''' 

#%% Fitting gaussian for the photon throughput plots 

# def gaussian(x, amp, cen, width, offset):
#     return amp * np.exp(-(x-cen)**2 / (2*width**2)) + offset
# # Initial guess for the parameters
# initial_guess = [20, 160, 60, 1e3]  # [amplitude, center, width, offset]

# # Example data generation
# x = nuv_wavelengths
# y = nuv_ratios

# # Fit the curve
# popt, pcov = curve_fit(gaussian, x, y, p0=initial_guess)

# # Extract the fitted parameters
# amp, cen, width, offset = popt

# # Calculate FWHM
# fwhm = 2.355 * width

# # Median x value (center of the Gaussian)
# median_x = cen

# # Print results
# print(f"Fitted parameters: Amplitude = {amp:.2f}, Center = {cen:.2f}, Width = {width:.2f}, Offset = {offset:.2f}")
# print(f"FWHM: {fwhm:.2f}")
# print(f"Median x value of the Gaussian: {median_x:.2f}")


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
        meas_err = fuv['Electron Error'][i].values[0]
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
        meas_err = nuv['Electron Error'][i].values[0]
        nuv_ratios.append(meas/incident)
        nuv_wavelengths.append(wv)

plt.figure()
plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Electrons/second')
plt.title('Payload Response: Electron Flux / normalized photodiode data')


#%% fitting gaussian to the normalized reponse plots

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
#         meas_err = fuv['Photon Error Estimate'][i].values[0]
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
#         meas_err = nuv['Photon Error Estimate'][i].values[0]
#         nuv_ratios.append(meas*100/incident)
#         nuv_wavelengths.append(wv)

# plt.figure()
# plt.semilogy(fuv_wavelengths,fuv_ratios,'-o')
# plt.semilogy(nuv_wavelengths,nuv_ratios,'-o')
# plt.xlabel('Wavelength (nm)')
# plt.ylabel('Throughput (%)')
# plt.title('Throughput vs Wavelength')
#%%A better way to do things
'''
Okay so what we are going to do here instead is calculate the 'system QE' and work
with those numbers. Basically do the same thing as before but rather than use the 
normalized response actually use the calculated values for photons in the aperture
and the error to get e/p for the payload as a whole
'''
def gaussian(x, amp, cen, width, offset):
    return amp * np.exp(-(x-cen)**2 / (2*width**2)) + offset
fuv_ratios = []
fuv_wavelengths = []
fuv_ratio_errors = []
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    incident = row['Adjusted Flux']
    inc_err = row['Adjusted Error']
    i = fuv['Wavelength (nm)']==int(wv)
    if len(fuv['Electrons/s'][i]) > 0:
        meas = fuv['Electrons/s'][i].values[0]
        meas_err = fuv['Electron Error'][i].values[0]
        ratio = (meas/incident)
        ratio_err = ratio*np.sqrt((meas_err/meas)**2+(inc_err/incident)**2)
        fuv_ratios.append(ratio)
        fuv_wavelengths.append(wv)
        fuv_ratio_errors.append(ratio_err)

nuv_ratios = []
nuv_wavelengths = []
nuv_ratio_errors = []
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    incident = row['Adjusted Flux']
    inc_err = row['Adjusted Error']
    i = nuv['Wavelength (nm)']==int(wv)
    if len(nuv['Electrons/s'][i]) > 0:
        meas = nuv['Electrons/s'][i].values[0]
        meas_err = nuv['Electron Error'][i].values[0]
        ratio = (meas/incident)
        ratio_err = ratio*np.sqrt((meas_err/meas)**2+(inc_err/incident)**2)
        nuv_ratios.append(ratio)
        nuv_wavelengths.append(wv)
        nuv_ratio_errors.append(ratio_err)

plt.figure(figsize=(12,10))
plt.subplot(211)
plt.errorbar(fuv_wavelengths,fuv_ratios,fuv_ratio_errors,8/2.355,fmt=':o',capsize=3,label='FUV')
plt.errorbar(nuv_wavelengths,nuv_ratios,nuv_ratio_errors,8/2.355,fmt=':^',capsize=3,label='NUV')
plt.xlabel('Wavelength (nm)')
plt.ylabel('SPARCS System Responsivity (e-/photon)')
plt.title('SPARCS Responsivity (linear) vs Wavelength')
plt.legend()
plt.subplot(212)
plt.errorbar(fuv_wavelengths,fuv_ratios,fuv_ratio_errors,8/2.355,fmt=':o',capsize=3,label='FUV')
plt.errorbar(nuv_wavelengths,nuv_ratios,nuv_ratio_errors,8/2.355,fmt=':^',capsize=3,label='NUV')
plt.yscale('log')
plt.xlabel('Wavelength (nm)')
plt.ylabel('SPARCS System Responsivity (e-/photon)')
plt.title('SPARCS Responsivity (log) vs Wavelength')
plt.legend()



# Initial guess for the parameters
initial_guess = [0.08, 160, 20, 0]  # [amplitude, center, width, offset]
# Example data generation
x = fuv_wavelengths
y = fuv_ratios
# Fit the curve
popt, pcov = curve_fit(gaussian, x, y, p0=initial_guess,sigma=np.array(fuv_ratios)/np.array(fuv_ratio_errors))
perr = np.sqrt(np.diag(pcov))
# Extract the fitted parameters
amp, cen, width, offset = popt
amp_err,cen_err,width_err,offset_err = perr
# Calculate FWHM
fwhm = 2.355 * width
fwhm_err = 2.355*width_err
# Median x value (center of the Gaussian)
median_x = cen
# Print results
print(f"FUV Fitted parameters: Amplitude = {amp:.2f}, Center = {cen:.2f}, Width = {width:.2f}, Offset = {offset:.2f}")
print(f"FUV FWHM: {fwhm:.2f} +/- {np.sqrt(2)*8/2.355:.2f}")
print(f"FUV Median x value of the Gaussian: {median_x:.2f} +/- {8/2.355:.2f}")
plt.figure()
plt.scatter(x, y, label='FUV Data')
plt.plot(x, gaussian(x, *popt), label='FUV Fitted Gaussian', color='red')
plt.legend()
plt.show()

# Initial guess for the parameters
initial_guess = [0.08, 280, 20, 0]  # [amplitude, center, width, offset]
# Example data generation
x = nuv_wavelengths
y = nuv_ratios
# Fit the curve
popt, pcov = curve_fit(gaussian, x, y, p0=initial_guess,sigma=np.array(nuv_ratios)/np.array(nuv_ratio_errors))
perr = np.sqrt(np.diag(pcov))
# Extract the fitted parameters
amp, cen, width, offset = popt
amp_err,cen_err,width_err,offset_err = perr
# Calculate FWHM
fwhm = 2.355 * width
fwhm_err = 2.355*width_err
# Median x value (center of the Gaussian)
median_x = cen
# Print results
print(f"NUV Fitted parameters: Amplitude = {amp:.2f}, Center = {cen:.2f}, Width = {width:.2f}, Offset = {offset:.2f}")
print(f"NUV FWHM: {fwhm:.2f} +/- {np.sqrt(2)*8/2.355:.2f}")
print(f"NUV Median x value of the Gaussian: {median_x:.2f}  +/- {8/2.355:.2f}")
plt.scatter(x, y, label='NUV Data')
plt.plot(x, gaussian(x, *popt), label='NUV Fitted Gaussian')
plt.legend()
plt.show()

#%% TRying the throguhput again with my own interpolation
# Interpolate the QE data myself instead of using David's stuff
fqe = fuv_qe['avg QE [%]']
fwv = fuv_qe['wav[nm]']
ferr = fuv_qe['error']
ff = interp1d(fwv,fqe)
fqe_new = ff(fuv_wavelengths)
fferr = interp1d(fwv,ferr)
ferr_new=fferr(fuv_wavelengths)
# plt.plot(fwv, fqe, 'o', fuv_wavelengths, fqe_new, '-x')
# plt.plot(fwv, ferr, 'o', fuv_wavelengths, ferr_new, '-x')

nqe = nuv_qe['ave QE [%]']
nwv = nuv_qe['wav [nm]']
nerr = nuv_qe['error']
nf = interp1d(nwv,nqe)
nqe_new = nf(nuv_wavelengths)
nferr = interp1d(nwv,nerr)
nerr_new=nferr(nuv_wavelengths)
# plt.plot(nwv, nqe, 'o', nuv_wavelengths, nqe_new, '-x')
# plt.plot(nwv, nerr, 'o', nuv_wavelengths, nerr_new, '-x')


ftp = fuv_ratios/(fqe_new/100)*100
ntp = nuv_ratios/(nqe_new/100)*100

ftp_err = ftp*np.sqrt((np.array(fuv_ratio_errors)/np.array(fuv_ratios))**2+(ferr_new/fqe_new)**2)
ntp_err = ntp*np.sqrt((np.array(nuv_ratio_errors)/np.array(nuv_ratios))**2+(nerr_new/nqe_new)**2)


plt.figure(figsize=(12,10))
plt.subplot(211)
plt.errorbar(fuv_wavelengths[:21],ftp[:21],abs(ftp_err[:21]),8/2.355,':o',capsize=3)
plt.errorbar(nuv_wavelengths,ntp,abs(ntp_err),8/2.355,':o',capsize=3)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Throughput (%)')
plt.title('Throughput vs Wavelength')
plt.yscale('log')
plt.subplot(212)
plt.errorbar(fuv_wavelengths[:21],ftp[:21],abs(ftp_err[:21]),8/2.355,':o',capsize=3)
plt.errorbar(nuv_wavelengths,ntp,abs(ntp_err),8/2.355,':o',capsize=3)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Throughput (%)')
plt.title('Throughput vs Wavelength')
#%%F it lets calculate the effective aperture too


feff_ap = []
feff_err=[]

for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    photon_flux = row['Photon Flux [Photons/s m^2]']*3.45e-3
    photon_flux_err = photon_flux*np.sqrt((row['Flux Error Estimate']/row['Photon Flux [Photons/s m^2]'])**2+(3.31E-04/3.45e-3)**2)
    i = fuv['Wavelength (nm)']==int(wv)
    if len(fuv['Electrons/s'][i]) > 0:
        meas = fuv['Electrons/s'][i].values[0]
        meas_err = fuv['Electron Error'][i].values[0]
        ratio = fuv_ratios[np.where(np.array(fuv_wavelengths)==wv)[0][0]]
        ratio_err = fuv_ratio_errors[np.where(np.array(fuv_wavelengths)==wv)[0][0]]
        eff_ap = meas/(photon_flux*ratio) * 10000
        feff_ap.append(eff_ap)
        eff_err = eff_ap*np.sqrt((meas_err/meas)**2+(ratio_err/ratio)**2+(photon_flux_err/photon_flux**2))
        feff_err.append(eff_err)

fefferr = 1/len(feff_err)*np.sqrt(np.sum(np.array(feff_err)**2)) #standard error

neff_ap = []
neff_err=[]
for index,row in photo.iterrows():
    wv = round(row['Wavelength [nm]'])
    photon_flux = row['Photon Flux [Photons/s m^2]']*3.45e-3
    photon_flux_err = photon_flux*np.sqrt((row['Flux Error Estimate']/row['Photon Flux [Photons/s m^2]'])**2+(3.31E-04/3.45e-3)**2)
    i = nuv['Wavelength (nm)']==int(wv)
    if len(nuv['Electrons/s'][i]) > 0:
        meas = nuv['Electrons/s'][i].values[0]
        meas_err = nuv['Electron Error'][i].values[0]
        ratio = nuv_ratios[np.where(np.array(nuv_wavelengths)==wv)[0][0]]
        ratio_err = nuv_ratio_errors[np.where(np.array(nuv_wavelengths)==wv)[0][0]]
        eff_ap = meas/(photon_flux*ratio) * 10000
        neff_ap.append(eff_ap)
        eff_err = eff_ap*np.sqrt((meas_err/meas)**2+(ratio_err/ratio)**2+(photon_flux_err/photon_flux**2))
        neff_err.append(eff_err)
        
nefferr = 1/len(neff_err)*np.sqrt(np.sum(np.array(neff_err)**2)) #standard error











