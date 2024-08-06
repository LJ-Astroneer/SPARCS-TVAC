# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 11:58:36 2024

@author: logan with Chat GPT-4 input 
"""

import os
import numpy as np
from astropy.io import fits

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

def subtract_overscan(image, overscan_region):
    """Subtract the bias level measured in the overscan region from the image."""
    # Calculate the median of the overscan region as the bias level
    overscan_level = np.median(image[overscan_region])
    # Subtract this bias level from the entire image
    image_corrected = image - overscan_level
    return image_corrected, overscan_level

def create_master_bias(bias_frames, overscan_region):
    """Create a master bias frame by subtracting overscan and taking the median all bias frames."""
    corrected_bias_frames = []
    overscan_levels = []
    for frame in bias_frames:
        corrected_frame, overscan_level = subtract_overscan(frame, overscan_region)
        corrected_bias_frames.append(corrected_frame)
        overscan_levels.append(overscan_level)
    master_bias = np.median(corrected_bias_frames, axis=0)
    return master_bias, overscan_levels

def create_master_dark(dark_frames, master_bias, overscan_region):
    """Create a master dark frame by subtracting overscan, subtracting the master bias, and then taking the median."""
    corrected_dark_frames = []
    overscan_levels = []
    for frame in dark_frames:
        corrected_frame, overscan_level = subtract_overscan(frame, overscan_region)
        calibrated_frame = corrected_frame - master_bias
        corrected_dark_frames.append(calibrated_frame)
        overscan_levels.append(overscan_level)
    master_dark = np.median(corrected_dark_frames, axis=0)
    return master_dark, overscan_levels

def create_header(input_headers, processing_steps, overscan_levels):
    """Create a FITS header for the output file."""
    output_header = input_headers[0].copy()
    
    # Add HISTORY lines for processing steps
    for step in processing_steps:
        output_header.add_history(step)
    
    # Add overscan levels to header
    output_header['OVSCLVL'] = (np.median(overscan_levels), 'median overscan level subtracted')
    
    return output_header

def save_fits(data, header, filename):
    """Save a 2D numpy array as a FITS file with a specified header."""
    hdu = fits.PrimaryHDU(data, header=header)
    hdu.writeto(filename, overwrite=True)

def main(bias_dir, dark_dir, output_dir, overscan_region):
    # Load bias frames and their headers
    print("Loading bias frames...")
    bias_frames, bias_headers = load_fits_files_with_headers(bias_dir)
    
    # Load dark frames and their headers
    print("Loading dark frames...")
    dark_frames, dark_headers = load_fits_files_with_headers(dark_dir)
    
    # Generate master bias frame
    print("Creating master bias frame...")
    master_bias, bias_overscan_levels = create_master_bias(bias_frames, overscan_region)
    bias_header = create_header(bias_headers, [
        "Overscan level subtracted from each bias frame.",
        "Master bias frame created by taking the median all bias frames."
    ], bias_overscan_levels)
    save_fits(master_bias, bias_header, os.path.join(output_dir, 'master_bias.fits'))
    
    # Generate master dark frame
    print("Creating master dark frame...")
    master_dark, dark_overscan_levels = create_master_dark(dark_frames, master_bias, overscan_region)
    dark_header = create_header(dark_headers, [
        "Overscan level subtracted from each dark frame.",
        "Master dark frame created by subtracting master bias from each dark frame.",
        "Master dark frame created by taking the median all calibrated dark frames."
    ], dark_overscan_levels)
    save_fits(master_dark, dark_header, os.path.join(output_dir, '1800sec_NUV_master_dark.fits'))
    
    print("Calibration files created successfully with headers!")

if __name__ == "__main__":
    # Directories for bias and dark frames
    bias_dir = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darksandbiases\20240605_-38C_darks_NUV\0sec"
    dark_dir = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darksandbiases\20240605_-38C_darks_NUV\1800sec"
    output_dir = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darksandbiases\20240605_-38C_darks_NUV\output"
    
    # Define the overscan region (e.g., overscan_region = slice(y1, y2), slice(x1, x2)) data[1:1033-8,1075:1075+96]
    # Adjust these slices according to your specific FITS file structure. 
    overscan_region = (slice(1, 1033-8), slice(1075,1075+96))  # Example for vertical overscan region
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the main process
    main(bias_dir, dark_dir, output_dir, overscan_region)
