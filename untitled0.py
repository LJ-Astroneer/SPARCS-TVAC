# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 15:12:33 2024

@author: logan
"""

import numpy as np

from astropy.modeling.models import Gaussian2D

from photutils.datasets import make_noise_image
import matplotlib.pyplot as plt
from astropy.visualization import simple_norm

gmodel = Gaussian2D(42.1, 47.8, 52.4, 4.7, 4.7, 0)

yy, xx = np.mgrid[0:100, 0:100]

data = gmodel(xx, yy)
#"C:\OneDrive - Arizona State University\SPARCS Documents\Logan Working\Phase1\phase1_photosandimages\20240322\FUV_FOV_fine\20240322_230136_FUV_FFI.fits"

error = make_noise_image(data.shape, mean=0., stddev=2.4, seed=123)

data += error

#%%
from photutils.centroids import centroid_quadratic

xycen = centroid_quadratic(data, xpeak=48, ypeak=52)

print(xycen)

#%%
from photutils.profiles import RadialProfile

edge_radii = np.arange(25)

rp = RadialProfile(data, xycen, edge_radii, error=error, mask=None)
plt.figure(0)
rp.plot(label='Radial Profile')

rp.plot_error()

norm = simple_norm(data, 'sqrt')
plt.figure(figsize=(5, 5))
plt.imshow(data, norm=norm)
rp.apertures[5].plot(color='C0', lw=2)
rp.apertures[10].plot(color='C1', lw=2)
rp.apertures[15].plot(color='C3', lw=2)

#%%
rp.gaussian_fit  
print(rp.gaussian_fwhm)  
plt.figure(0)
plt.plot(rp.radius, rp.gaussian_profile, label='Gaussian Fit')
plt.legend()


#%%
from photutils.profiles import CurveOfGrowth

radii = np.arange(1, 26)

cog = CurveOfGrowth(data, xycen, radii, error=error, mask=None)

plt.figure()
cog.plot(label='Curve of Growth')

cog.plot_error()

norm = simple_norm(data, 'sqrt')
plt.figure(figsize=(5, 5))
plt.imshow(data, norm=norm)
cog.apertures[5].plot(color='C0', lw=2)
cog.apertures[10].plot(color='C1', lw=2)
cog.apertures[15].plot(color='C3', lw=2)

#%%
cog.normalize(method='max')

ee_vals = cog.calc_ee_at_radius([5, 10, 15])  

ee_vals
