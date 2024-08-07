# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 18:16:35 2024

@author: logan
"""

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def gaussian_2d(coords, x0, y0, sigma_x, sigma_y, amplitude, theta, offset):
    x, y = coords
    xo = float(x0)
    yo = float(y0)
    a = (np.cos(theta)**2) / (2 * sigma_x**2) + (np.sin(theta)**2) / (2 * sigma_y**2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
    c = (np.sin(theta)**2) / (2 * sigma_x**2) + (np.cos(theta)**2) / (2 * sigma_y**2)
    return offset + amplitude * np.exp(- (a * (x - xo)**2 + 2 * b * (x - xo) * (y - yo) + c * (y - yo)**2))

def measure_fwhm(image_data, x_star, y_star, box_size=20):
    # Define a small box around the star to fit the Gaussian
    x_min = int(max(x_star - box_size // 2, 0))
    x_max = int(min(x_star + box_size // 2, image_data.shape[1]))
    y_min = int(max(y_star - box_size // 2, 0))
    y_max = int(min(y_star + box_size // 2, image_data.shape[0]))
    
    sub_image = image_data[y_min:y_max, x_min:x_max]
    
    # Create a grid of coordinates
    y, x = np.mgrid[y_min:y_max, x_min:x_max]
    
    # Flatten the grid and the image data
    coords = np.vstack((x.ravel(), y.ravel()))
    sub_image_flat = sub_image.ravel()
    
    # Initial guess for the Gaussian parameters
    initial_guess = (x_star, y_star, 3, 3, np.max(sub_image), 0, np.median(sub_image))
    
    # Fit a 2D Gaussian to the star's brightness profile
    try:
        popt, _ = curve_fit(gaussian_2d, coords, sub_image_flat, p0=initial_guess)
        x0, y0, sigma_x, sigma_y, amplitude, theta, offset = popt
        
        # FWHM is related to the standard deviation by FWHM = 2.3548 * sigma
        fwhm_x = 2.3548 * sigma_x
        fwhm_y = 2.3548 * sigma_y
        fwhm = np.sqrt(fwhm_x**2 + fwhm_y**2) / np.sqrt(2)  # Average FWHM
        
        return fwhm
    except RuntimeError:
        print("Fitting failed, could not determine FWHM.")
        return None

# Example usage
# image_data = np.random.rand(100, 100)  # Replace with actual image data
x_star, y_star = x, y  # Replace with actual coordinates

fwhm = measure_fwhm(image_data, x_star, y_star)
if fwhm:
    print(f"The FWHM of the star is: {fwhm:.2f} pixels")
