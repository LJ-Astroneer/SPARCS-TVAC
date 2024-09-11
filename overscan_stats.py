# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 11:20:26 2024

@author: logan
"""

import os
import csv
import numpy as np
from astropy.io import fits
from scipy.stats import median_abs_deviation

def process_fits_files_in_folders(folders, overscan_region = (slice(8, 1030), slice(1076,1170)), output_csv='combined_overscan_statistics.csv'):
    """
    Processes FITS files in multiple folders, measuring the mean, median, 
    standard deviation, and median absolute deviation (MAD) of the pixels 
    in the overscan region, and saves the combined results to a single CSV file.

    Parameters:
    folders (list of str): List of paths to the folders containing the FITS files.
    overscan_region (tuple of slices): Region in the image data corresponding to the overscan.
    output_csv (str): Filename for the combined output CSV file.
    
    Returns:
    None
    """
    combined_statistics = []
    
    for folder_path in folders:
        for filename in os.listdir(folder_path):
            if filename.endswith('.fits'):
                file_path = os.path.join(folder_path, filename)
                with fits.open(file_path) as hdul:
                    image_data = hdul[0].data.astype(float)
                    
                    # Extract the overscan region
                    overscan_data = image_data[overscan_region]
                    
                    # Calculate statistics
                    mean_value = np.mean(overscan_data)
                    median_value = np.median(overscan_data)
                    std_value = np.std(overscan_data)
                    mad_value = median_abs_deviation(overscan_data.flatten())
                    
                    # Store the results
                    stats = {
                        'folder': os.path.dirname(folder_path),
                        'filename': filename,
                        'mean': mean_value,
                        'median': median_value,
                        'std': std_value,
                        'mad': mad_value
                    }
                    combined_statistics.append(stats)
    
    # Save combined statistics to a CSV file
    with open(output_csv, mode='w', newline='') as csvfile:
        fieldnames = ['folder', 'filename', 'mean', 'median', 'std', 'mad']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for stat in combined_statistics:
            writer.writerow(stat)
    
    print(f"Combined statistics saved to {output_csv}")

# Example usage
folders = [r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240605_-38C_darks_NUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240531_20C_darks_FUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240531_20C_darks_NUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240603_-32C_darks_FUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240603_-32C_darks_NUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240604_-35C_darks_FUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240604_-35C_darks_NUV/0sec",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240605_-38C_darks_FUV/0sec"]  # Replace with paths to your folders
folders = []

overscan_region = (slice(8, 1030), slice(1076,1170))  # Adjust if your overscan region is different

output_csv = r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/combined_overscan_statistics.csv"  # Specify your desired output file name

# Process the folders and save the combined results
process_fits_files_in_folders(folders, overscan_region, output_csv)
