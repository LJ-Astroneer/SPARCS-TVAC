# -*- coding: utf-8 -*-
"""
Created on Mon May  9 13:23:37 2022

@author: Logan Jensen

This code controls the UV monochromator and I wrote it all in an afternoon so ya,
I'll take my job at Goddard now thank you very much'

UV monochrtomator parameters:
    2nm/revolution control
    36000 steps/revolution
    so that is 18,000 steps/nm
    default V = 60,000 steps/sec = 210 nm/min
"""

import time
import serial

ser = serial.Serial(
    	port='COM3',
    	baudrate=9600,
    	parity=serial.PARITY_NONE,
    	stopbits=serial.STOPBITS_ONE,
    	bytesize=serial.EIGHTBITS,
        timeout=5
    )

print(ser.isOpen())

def read(ser):
    out = ''
    while ser.inWaiting() > 0:
        response = ser.read(1)
        response = response.decode("ascii")
        out += response
    if out != '':	
      print(out)

ser.write(b' \r\n') #always start with a space, should return a #, initializes the device
time.sleep(1)
ser.write(b'X\r\n') #reads current state of variables
time.sleep(1)
print(read(ser))

def move(nm):
    steps = int(nm*18000)
    if steps < 0:
        command = str(steps)+'\r\n'
        #print(command.encode())
        ser.write(command.encode())
    else:
        command = '+'+str(steps)+'\r\n'
        #print(command.encode())
        ser.write(command.encode())
        
def test_move(nm):
    steps = int(nm*18000)
    if steps < 0:
        command = str(steps)+'\r\n'
        print(command.encode())
    else:
        command = '+'+str(steps)+'\r\n'
        print(command.encode())


#%% Below is an example of what a wavelength scan would look like, used as the basis for wavelength_scan.py
# current = float(input('Current Wavelength?\n'))
# start = float(input('Starting Wavelegnth?\n'))
# step = float(input('Step?\n'))
# end = float(input('Final Wavelength?\n'))
# if end < start:
#     step = step*-1

# #get to starting location
# to_start = int((start-current))
# if to_start != 0:
#     move(to_start)
#     time.sleep(abs(to_start*1.5))

# #loop through the steps
# wv = start
# while wv <= end:
#     print('Reading at {:.2f}'.format(wv))
#     time.sleep(10) #readout of the photodiode takes about 6.1 seconds, 7 for margin
#     move(step)
#     wv+=step
#     time.sleep(1.5*abs(step)) #small steps are slow on the mono
#     # if abs(step) <= 10: 
#     #     time.sleep(1.5*abs(step)) #small steps are slow on the mono
#     # else:
#     #     time.sleep(0.6*abs(step)) #60,000 steps/sec = 0.3 s/nm so 0.6 for margin



#%%
# def mono_connect():
#     ser = serial.Serial(
#     	port='COM3',
#     	baudrate=9600,
#     	parity=serial.PARITY_NONE,
#     	stopbits=serial.STOPBITS_ONE,
#     	bytesize=serial.EIGHTBITS,
#         timeout=5
#     )

#     print(ser.isOpen())
#     return ser

# def hello():
#     ser = mono_connect()
#     ser.write(b' \r\n')
#     time.sleep(1)   
   
#     out = ''
#     while ser.inWaiting() > 0:
#         response = ser.read(1)
#         response = response.decode("utf-8")
#         out += response
#     if out != '':	
#       print(out)
#     return out
