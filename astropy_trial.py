# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 13:08:27 2024

@author: logan
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.io import fits
from matplotlib.colors import LogNorm
from matplotlib import colors
from scipy import stats

folder = '20240222\FUV\dark_subtracted'
BAND = ['FUV']#,'NUV']
for BAND in BAND:
    path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\\"+folder+"\\"+BAND+"_photometry_Measurements_adaptive.csv"
    df = pandas.read_csv(path,delimiter=',')
    fwhm = df['Width_T1']
    x = df['X(FITS)_T1']
    y = df['Y(FITS)_T1']
    snr = df['Source_SNR_T1']
    FOV_center = 500,500 #working assumption for now
    r = np.sqrt((x-FOV_center[0])**2+(y-FOV_center[1])**2) #finding the radius from the center for all images
    index = np.where(r==min(r))[0][0] #right now I just want to choose the center most image
    
    for i in [index]:
        row = df.iloc[i]    #just collects all the info from that row
        file = row['Label'] #filename
        path = r"D:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\phase1_photosandimages\\"+folder+"\\"+file
        image_file = astropy.io.fits.open(path, cache=True) #open fit
        image_data = fits.getdata(path) #get data
        image_data = image_data[:,:1065] #trim off the overscan
        x = int(row['X(FITS)_T1']) #all the X centroids 
        y = int(row['Y(FITS)_T1']) #all the Y centroids
#%% https://photutils.readthedocs.io/en/stable/aperture.html   
from photutils.aperture import aperture_photometry
from astropy.stats import sigma_clipped_stats
from photutils.aperture import ApertureStats, CircularAperture
from photutils.background import Background2D

positions = [x,y]
aperture = CircularAperture(positions, r=10.0) #adding method = 'center' will take pixels as being either wholly in or out of the aperture by their center position
data = image_data
phot_table = aperture_photometry(data, aperture)
phot_table['aperture_sum'].info.format = '%.8g'  # for consistent table output
print(phot_table)

'''
to do with multiple apertures at each location
radii = [3.0, 4.0, 5.0]
apertures = [CircularAperture(positions, r=r) for r in radii]
phot_table = aperture_photometry(data, apertures)
for col in phot_table.colnames:
    phot_table[col].info.format = '%.8g'  # for consistent table output
print(phot_table)
'''
#this is how you can get aperture stats
aperstats = ApertureStats(data, aperture)          
print(aperstats.mean, aperstats.median, aperstats.std)  

#this method makes a 2D background map
#https://photutils.readthedocs.io/en/stable/api/photutils.background.Background2D.html#photutils.background.Background2D
bkg = Background2D(image_data,100)       
plt.figure()
plt.imshow(bkg.background)

data_sub = data-bkg.background #subtract that background off
  
phot_table = aperture_photometry(data_sub, aperture)
phot_table['aperture_sum'].info.format = '%.8g'  # for consistent table output
print(phot_table)                
aperstats = ApertureStats(data_sub, aperture)          
print(aperstats.mean, aperstats.median, aperstats.std)  

#%% Copied code direclty from the photutils docs to make really nice aperture images
#https://photutils.readthedocs.io/en/stable/aperture.html
import matplotlib.pyplot as plt
from astropy.visualization import simple_norm
from photutils.aperture import CircularAnnulus, CircularAperture
from photutils.datasets import make_100gaussians_image

data = image_data
positions = [x,y]
aperture = CircularAperture(positions, r=10)
annulus_aperture = CircularAnnulus(positions, r_in=40, r_out=80)

norm = simple_norm(data, 'sqrt', percent=99)
plt.imshow(data, norm=norm, interpolation='nearest')

ap_patches = aperture.plot(color='white', lw=2,
                           label='Photometry aperture')
ann_patches = annulus_aperture.plot(color='red', lw=2,
                                    label='Background annulus')
handles = (ap_patches[0], ann_patches[0])
plt.legend(loc=(0.17, 0.05), facecolor='#458989', labelcolor='white',
           handles=handles, prop={'weight': 'bold', 'size': 11})

#code to find the mean value of the background in the annulus        
from photutils.aperture import ApertureStats       
aperstats = ApertureStats(data, annulus_aperture)
bkg_mean = aperstats.mean
print(bkg_mean)         

#now do the photometry for the circular aperture
from photutils.aperture import aperture_photometry
phot_table = aperture_photometry(data, aperture)
for col in phot_table.colnames:
    phot_table[col].info.format = '%.8g'  # for consistent table output
print(phot_table)
aperture_area = aperture.area_overlap(data)
print(aperture_area)  

total_bkg = bkg_mean * aperture_area
print(total_bkg) 

phot_bkgsub = phot_table['aperture_sum'] - total_bkg
phot_table['total_bkg'] = total_bkg
phot_table['aperture_sum_bkgsub'] = phot_bkgsub
for col in phot_table.colnames:
    phot_table[col].info.format = '%.8g'  # for consistent table output
print(phot_table)

#%% Radial profile from photutils
#naturally there is a code for centroid finding
from photutils.centroids import centroid_quadratic
xycen = centroid_quadratic(data)
print(xycen)  

#time for a radial profile
from photutils.profiles import RadialProfile
edge_radii = np.arange(10)
rp = RadialProfile(data, xycen, edge_radii, mask=None)
rp.plot(label='Radial Profile')
rp.gaussian_fit  
print(rp.gaussian_fwhm)


#%%curve of growth

from photutils.profiles import CurveOfGrowth
#radii = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5]
radii = [1,2,3,4,5,6,7,8,9,10,30]
cog = CurveOfGrowth(image_data, xycen, radii, mask=None,method='exact')

#normalize it to 1
cog.normalize()
plt.plot(cog.radius,cog.profile,'-o')
#plt.ylim((0,1.2))


#%% Try to do manual aperture photometry to get a curve of growth with local background subtractions

data = image_data #data_sub
positions = [x,y]
radii = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5]
apertures = [CircularAperture(positions, r=r) for r in radii]
annulus_aperture = CircularAnnulus(positions, r_in=40, r_out=80)

#code to find the mean value of the background in the annulus        
from photutils.aperture import ApertureStats       
aperstats = ApertureStats(data, annulus_aperture)
bkg_mean = aperstats.mean
print(bkg_mean)         

#now do the photometry for the circular apertures
from photutils.aperture import aperture_photometry
phot_table = aperture_photometry(data, apertures)
for col in phot_table.colnames:
    phot_table[col].info.format = '%.8g'  # for consistent table output
print(phot_table)

aperture_area=[]
total_bkg=[]
sums=[]
for ap in apertures:
    s = aperture_photometry(data,ap)['aperture_sum'][0]
    sums.append(s)
    area = ap.area_overlap(data)
    aperture_area.append(area)
    total_bkg.append(bkg_mean * area)
 
sums_bkg = [a_i - b_i for a_i, b_i in zip(sums, total_bkg)]
ratios = [c_i/sums_bkg[-1] for c_i in sums_bkg]

rad = [x*13 for x in radii]

plt.figure(1) 
plt.plot(rad,ratios,'-o')
plt.title(BAND+' Enclosed energy')
plt.xlabel('Radius (um)')
plt.ylabel('Fractional enclosed energy')
plt.ylim((0,1.1))

temp = annulus_aperture.to_mask().get_values(data)
dark = temp#image_data[darkmask!=0] #take all the image pixels in that annulus
dark_median = np.median(dark) #median  of the dark
dark_mean = np.mean(dark)
dark_mode = stats.mode(dark)[0]
dark_std = np.std(dark) #std of the dark
#to be extra fancy we are going to implement a 3sigma cutoff a la Howell to improve the stats
dark_cutoff = dark[(dark > dark_median-3*dark_std) & (dark < dark_median+3*dark_std)]
cutoff_num = len(dark) - len(dark_cutoff) #just to have as a reference of how many pixels fell outside of this range
dark_median = np.median(dark_cutoff) #median of the dark
dark_mean = np.mean(dark_cutoff)
dark_pix = dark_mean


#make a nice plot of background distribution for stats
plt.figure(2)
plt.hist(dark_cutoff,bins='auto') #Statistics, show a nice plot for the dark current
plt.title('Distributaiton of Background Pixels')
plt.xlabel('Pixel value')
plt.legend(['Mean = {:.1f}, Std. Dev. = {:.1f}'.format(dark_median,dark_std)])



        
        
        