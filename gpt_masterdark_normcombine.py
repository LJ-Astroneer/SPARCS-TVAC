# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:26:15 2024

@author: logan
"""
import os
from astropy.io import fits
import numpy as np

def normalize_fits_files(directory):
    # Get a list of all FITS files in the directory
    fits_files = [f for f in os.listdir(directory) if f.endswith('.fits')]
    
    normalized_data = []
    
    for file in fits_files:
        # Load the FITS file
        file_path = os.path.join(directory, file)
        with fits.open(file_path) as hdul:
            # Extract the image data
            image_data = hdul[0].data
            # Extract the exposure time from the header
            exposure_time = hdul[0].header['EXPTIME']
            # Normalize the image data by the exposure time
            normalized_image_data = image_data / exposure_time
            
            # Add a HISTORY entry in the header
            hdul[0].header.add_history(f"Image normalized by exposure time: {exposure_time} seconds")
            hdul[0].header.add_history(f"File normalized on {fits.getval(file_path, 'DATE-OBS')}")
            
            # Save the normalized image data to a new FITS file
            normalized_filename = f'normalized_{file}'
            fits.writeto(os.path.join(directory, normalized_filename), normalized_image_data, hdul[0].header, overwrite=True)
            
            normalized_data.append(normalized_image_data)
    
    return normalized_data

# Usage example
directory = r'C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darksandbiases/20240605_-38C_darks_NUV/output'
normalized_images = normalize_fits_files(directory)
