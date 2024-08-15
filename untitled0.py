import os
import csv
import numpy as np
from astropy.io import fits
from scipy.stats import median_abs_deviation

def process_overscan_statistics(folder_path, overscan_region=(slice(1033-7,1033), slice(0,1175)), output_csv='overscan_statistics.csv'):
    """
    Processes a batch of FITS files in a folder, measuring the mean, median, 
    standard deviation, and median absolute deviation (MAD) of the pixels 
    in the overscan region, and saves the results to a CSV file.

    Parameters:
    folder_path (str): Path to the folder containing the FITS files.
    overscan_region (tuple of slices): Region in the image data corresponding to the overscan.
    output_csv (str): Filename for the output CSV file.
    
    Returns:
    None
    """
    statistics = []
    
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
                mad_value = median_abs_deviation(overscan_data)
                
                # Store the results
                stats = {
                    'filename': filename,
                    'mean': mean_value,
                    'median': median_value,
                    'std': std_value,
                    'mad': mad_value
                }
                statistics.append(stats)
    
    # Save statistics to a CSV file
    with open(output_csv, mode='w', newline='') as csvfile:
        fieldnames = ['filename', 'mean', 'median', 'std', 'mad']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for stat in statistics:
            writer.writerow(stat)
    
    print(f"Statistics saved to {output_csv}")

# Example usage
for folder in [r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240605_-38C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240531_20C_darks_FUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240531_20C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240603_-32C_darks_FUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240603_-32C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240604_-35C_darks_FUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240604_-35C_darks_NUV",
r"C:/OneDrive - Arizona State University/SPARCS Documents/Logan Working/Phase2/Data/gpt_darkandbias_overscan2.1/20240605_-38C_darks_FUV"]:
    folder_path = folder+"\\0sec"  # Replace with the path to your folder
    overscan_region = (slice(1033-7,1033), slice(0,1175))  # Adjust if your overscan region is different
    output_csv = folder_path[:-4]+'overscan_statistics.csv'  # Specify your desired output file name
    
    # Process the files and save the results
    process_overscan_statistics(folder_path, overscan_region, output_csv)