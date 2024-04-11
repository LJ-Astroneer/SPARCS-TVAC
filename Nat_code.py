# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 16:08:08 2024

@author: logan
"""

from astropy.io.fits import getdata
from scipy.ndimage import median_filter
from numpy import *
from matplotlib.pyplot import *

# science image
x = getdata('20240222_173957_FUV_FFI.fits')*1.

#overscans
col = median(x[:,1065:1167],axis=1)
xT = x.T
xT-=col
row = median(x[-7:],axis=0)
x-=row

# dark image
x0=getdata('MED_FUV_dark_10s.fits')*1.
x0T = x0.T
x0T-=col
row = median(x0[-7:],axis=0)
x0-=row

# scale dark
f = median(x[:-7,22:1064]) / median(x0[:-7,22:1064])
x -= f*x0
# subtract background (very slow)
bg = median_filter(x,71)
x-=bg
xrms = 1.48*median(abs(x[:-7,22:1064]))  # rms of background

# find centroid, x0,y0
i,j=442,516
sz=5
xt = 1.*x[i-sz:i+sz+1,j-sz:j+sz+1]
xx = arange(2*sz+1)-sz
x0 = dot(xx,xt).sum()/xt.sum()
y0 = dot(xt,xx).sum()/xt.sum()

# make a thumbnail, and oversample
sz=10
xt = 1.*x[i-sz:i+sz+1,j-sz:j+sz+1]
oversamp=5
sz1 = 2*sz+1
xt1 = zeros( (sz1*oversamp,sz1*oversamp),dtype='float32')
for i in range(sz1):
    for j in range(sz1):
        xt1[i*oversamp:(1+i)*oversamp,j*oversamp:(j+1)*oversamp] = xt[i,j]

# x and y arrays for oversampled image
xx = (arange(sz1*oversamp)-(sz1*oversamp)//2)/oversamp-x0
yy = (arange(sz1*oversamp)-(sz1*oversamp)//2)/oversamp-y0

# radius image
rad = sqrt(xx[:,newaxis]**2+(yy[newaxis,:]**2))
s=rad.flatten().argsort()
mx = xt1.flatten()[s].cumsum()[-1]
plot (rad.flatten()[s],xt1.flatten()[s].cumsum()/mx)
xlim((0,4))
xlabel("Radius [pixels]",fontsize=14)
ylabel("Encircled Energy",fontsize=14)