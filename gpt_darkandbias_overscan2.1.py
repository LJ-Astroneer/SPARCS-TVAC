# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 11:58:36 2024

@author: logan with Chat GPT-4 input 

Code to work through the creating of master bias and master dark images for each temparture and each exposure time
You have to manually change the folder each time to adjust for the exposures
The difference in the overscan is that now there is a subtraction of the median column from the overscan column and a median row from the overscan row

"""

import os
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def load_fits_files_with_headers(directory):
    """Load all FITS files and their headers in a given directory."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.fits')]
    images = []
    headers = []
    for f in files:
        hdul = fits.open(f)
        images.append(hdul[0].data)
        headers.append(hdul[0].header)
        hdul.close()
    return np.array(images), headers

def subtract_overscan(image, overscan_region,overscan_region2):
    """Subtract the bias level measured in the overscan region from the image."""
    # Calculate the median of the overscan region as the bias level
    # Extract the overscan region
    overscan_region = image[overscan_region]
    
    # Calculate the median value for each row in the overscan region
    median_column = np.median(overscan_region, axis=1)
    # Subtract the median column from each column of the image
    corrected_image = image - median_column[:, None]
    
    # overscan_region2 = corrected_image[overscan_region2]
    # median_row = np.median(overscan_region2, axis=0)
    # median_row = gaussian_filter1d(median_row,sigma=6)
    # corrected_image = corrected_image - median_row[None,:]
    
    return corrected_image

def create_master_bias(bias_frames, overscan_region,overscan_region2):
    """Create a master bias frame by subtracting overscan and taking the median all bias frames."""
    corrected_bias_frames = []
    
    for frame in bias_frames:
        corrected_frame= subtract_overscan(frame, overscan_region,overscan_region2)
        corrected_bias_frames.append(corrected_frame)
    master_bias = np.median(corrected_bias_frames, axis=0)
    return master_bias

def create_master_dark(dark_frames, master_bias, overscan_region,overscan_region2):
    """Create a master dark frame by subtracting overscan, subtracting the master bias, and then taking the median."""
    corrected_dark_frames = []
    
    for frame in dark_frames:
        corrected_frame = subtract_overscan(frame, overscan_region,overscan_region2)
        calibrated_frame = corrected_frame - master_bias
        corrected_dark_frames.append(calibrated_frame)
    master_dark = np.median(corrected_dark_frames, axis=0)
    return master_dark

def create_header(input_headers, processing_steps):
    """Create a FITS header for the output file."""
    output_header = input_headers[0].copy()
    
    # Add HISTORY lines for processing steps
    for step in processing_steps:
        output_header.add_history(step)
    
    
    return output_header

def save_fits(data, header, filename):
    """Save a 2D numpy array as a FITS file with a specified header."""
    hdu = fits.PrimaryHDU(data, header=header)
    hdu.writeto(filename, overwrite=True)

def main(bias_dir, dark_dir, output_dir, overscan_region,overscan_region2,subfolder):
    # Load bias frames and their headers
    print("Loading bias frames...")
    bias_frames, bias_headers = load_fits_files_with_headers(bias_dir)
    
    # Load dark frames and their headers
    print("Loading dark frames...")
    dark_frames, dark_headers = load_fits_files_with_headers(dark_dir)
    
    # Generate master bias frame
    print("Creating master bias frame...")
    master_bias = create_master_bias(bias_frames, overscan_region,overscan_region2)
    bias_header = create_header(bias_headers, [
        "Overscan level subtracted from each bias frame.",
        "Master bias frame created by taking the median all bias frames."
    ])
    save_fits(master_bias, bias_header, os.path.join(output_dir, 'master_bias.fits'))
    
    # Generate master dark frame
    print("Creating master dark frame...")
    master_dark = create_master_dark(dark_frames, master_bias, overscan_region,overscan_region2)
    dark_header = create_header(dark_headers, [
        "Overscan level subtracted from each dark frame.",
        "Master dark frame created by subtracting master bias from each dark frame.",
        "Master dark frame created by taking the median all calibrated dark frames."
    ])
    save_fits(master_dark, dark_header, os.path.join(output_dir, subfolder+'_master_dark.fits'))
    
    print("Calibration files created successfully with headers!")


for folder in [r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240605_-38C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240531_20C_darks_FUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240531_20C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240603_-32C_darks_FUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240603_-32C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240604_-35C_darks_FUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240604_-35C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240605_-38C_darks_FUV"]:
    for subfolder in ['0sec','30sec','60sec','300sec','600sec','1800sec']:
        if __name__ == "__main__":
            # Directories for bias and dark frames
            # bias_dir = r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.0/20240531_20C_darks_FUV/0sec"
            bias_dir = folder+'//0sec'
            # dark_dir = r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.0/20240531_20C_darks_FUV/1800sec"
            dark_dir = folder+'//'+subfolder
            # output_dir = r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.0/20240531_20C_darks_FUV/output"
            output_dir = folder+'//output'
            # Define the overscan region (e.g., overscan_region = slice(y1, y2), slice(x1, x2)) data[1:1033-8,1075:1075+96]
            # Adjust these slices according to your specific FITS file structure. 
            overscan_region = (slice(0, 1033), slice(1076,1170))
            overscan_region2= (slice(1033-7,1033), slice(0,1175))
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Run the main process
            main(bias_dir, dark_dir, output_dir, overscan_region,overscan_region2,subfolder)
