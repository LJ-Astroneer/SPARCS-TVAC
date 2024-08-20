# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 13:08:43 2024

@author: logan
"""

import os
import numpy as np
from astropy.io import fits

def process_fits_file(input_file, master_bias, master_dark, output_folder):
    with fits.open(input_file) as hdul:
        image_data = hdul[0].data.astype(float)
        header = hdul[0].header

        # Subtract the overscan bias (assuming overscan in the last 50 columns)
        overscan_region = (slice(0, 1033), slice(1076,1170))
        overscan_region = image_data[overscan_region]
        # Calculate the median value for each row in the overscan region
        overscan_median_column = np.median(overscan_region, axis=1)
        image_data = image_data - overscan_median_column[:, None]
        header.add_history(f"Overscan bias median column {overscan_median_column} subtracted from image.")

        # Subtract the master bias
        image_data -= master_bias
        header.add_history("Master bias frame subtracted from image.")

        # Get the exposure time of the input image
        exposure_time = header.get('EXPTIME', 1)  # Default to 1 if EXPTIME not found

        # Scale the master dark by the exposure time
        scaled_master_dark = master_dark * exposure_time

        # Subtract the scaled master dark
        image_data -= scaled_master_dark
        header.add_history(f"Master dark frame scaled by exposure time ({exposure_time:.2f} s) and subtracted from image.")


        # Save the processed file to the output folder
        output_file = os.path.join(output_folder, os.path.basename(input_file))
        hdu = fits.PrimaryHDU(image_data, header=header)
        hdulist = fits.HDUList([hdu])
        hdulist.writeto(output_file, overwrite=True)

def process_folder(input_folder, master_bias_file, master_dark_file, output_folder):
    # Load the master bias and dark files
    master_bias = fits.getdata(master_bias_file).astype(float)
    master_dark = fits.getdata(master_dark_file).astype(float)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each FITS file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.fits'):
            input_file = os.path.join(input_folder, filename)
            process_fits_file(input_file, master_bias, master_dark, output_folder)
            print(f"Processed {filename}")

# Example usage
input_folder = r'C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/Throughput/NUV all samples'
master_bias_file = r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darkandbias_overscan2.1\20240604_-35C_darks_NUV\output\master_bias.fits"
master_dark_file = r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darkandbias_overscan2.1\20240604_-35C_darks_NUV\output\normalized_1800sec_master_dark.fits"
output_folder = r"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\Throughput\NUV all samples processed"

process_folder(input_folder, master_bias_file, master_dark_file, output_folder)
