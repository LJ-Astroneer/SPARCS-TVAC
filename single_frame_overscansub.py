import numpy as np
from astropy.io import fits
from scipy.ndimage import gaussian_filter

def overscan_subtract(image_data, overscan_region,overscan_region2):
    """
    Perform overscan subtraction on FITS image data.

    Parameters:
    image_data (numpy.ndarray): The 2D image data array.
    overscan_start_col (int): The starting column index of the overscan region.
    overscan_end_col (int): The ending column index of the overscan region.

    Returns:
    numpy.ndarray: The overscan-subtracted image data.
    """
    # Extract the overscan region
    overscan_region = image_data[overscan_region]
    
    # Calculate the median value for each row in the overscan region
    median_column = np.median(overscan_region, axis=1)
    
    # Subtract the median column from each column of the image
    corrected_image = image_data - median_column[:, None]
    
    overscan_region2 = corrected_image[overscan_region2]
    median_row = np.median(overscan_region2, axis=0)
    corrected_image = corrected_image - median_row[None,:]
    
    return corrected_image

# Example usage
image_file = r'C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darkandbias_overscan2.0\20240605_-38C_darks_NUV\0sec\20240605_173622_NUV_FFI.fits'
with fits.open(image_file) as hdul:
    image_data = hdul[0].data.astype(float)
    header = hdul[0].header

# Define the overscan region (e.g., columns 1024 to 1050)
overscan_region = (slice(0, 1033), slice(1076,1170))
overscan_region2= (slice(1033-7,1033), slice(0,1175))

# Perform the overscan subtraction
corrected_image = overscan_subtract(image_data, overscan_region,overscan_region2)

# Save the corrected image
hdu = fits.PrimaryHDU(corrected_image, header=header)
hdul = fits.HDUList([hdu])
hdul.writeto(r'C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase2\Data\gpt_darkandbias_overscan2.0\20240605_-38C_darks_NUV\test2.fits', overwrite=True)
