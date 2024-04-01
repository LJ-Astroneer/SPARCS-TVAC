# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:18:30 2024

@author: logan
"""

import numpy as np
np.sin
pi = np.pi
delta = 10/3600*pi/180 #10"
alpha = pi/4 #45°
t = 13 #mm
n = 1.46 #at 533nm for fused silica
lamd = 533e-6 #mm
f = 547 #mm for bench telescope 547 for SPARCS
fn = 6 #f/13.9 for bench telescope
pix = 13e-3 #mm 3.45um pixels for bench telescope

s = t*np.sin(2*alpha)/np.sqrt(((n**2-np.sin(alpha)**2))) #10.18 mm
theta = 2*delta*np.sqrt((n**2-np.sin(alpha)**2)) #0.0012385 rad

d = lamd/theta #4.3mm

def R(phi_deg):
    phi = phi_deg*pi/180
    R = -s/(theta*np.tan(phi)) #mm
    return R

def phi(R):
    phi = np.arctan(-s/(theta*R)) #radians
    phi_deg = phi*180/pi
    return phi_deg

def defocus(R):
    defocus = f**2/R #linear defocus distance
    return defocus

def spot(defocus):
    spot = defocus/fn/pix #size of spot in pixels
    return spot
#%%
R = -s/(theta*np.tan(phi)) #mm
phi = np.arctan(-s/(theta*R)) #radians
phi_deg = phi*180/pi #degrees


defocus = f**2/R #linear defocus distance
spot = defocus/fn/pix #size of spot in pixels


df = 95.13 #mm measured farthest diameter
di = 96.12 #mm measured nearest diameter
l = 4739 #mm separation between measurements
divergence = 2*np.arctan((df-di)/2/l) #rad
curve = df/divergence #mm
