# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 15:59:41 2022

@author: Logan Jensen
"""
import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
def vacconnect():
    ser = serial.Serial(
    	port='COM10',
    	baudrate=9600,
    	parity=serial.PARITY_NONE,
    	stopbits=serial.STOPBITS_ONE,
    	bytesize=serial.EIGHTBITS,
        timeout=5
    )

    print(ser.isOpen())
    return ser

def read_pres(ser):
    ser.write(b'#0002UTURBO\r\n')
    time.sleep(1)   
   
    out = ''
    # loop which reads out mean and stddev when calculations are finished
    while ser.inWaiting() > 0:
        response = ser.read(2)
        response = response.decode("utf-8")
        out += response
    if out != '':	
      print(out)
    return out

def read_dry(ser):
    ser.write(b'#0002UDRY\r\n')
    time.sleep(2)   
   
    out = ''
    # loop which reads out mean and stddev when calculations are finished
    while ser.inWaiting() > 0:
        response = ser.read(1)
        response = response.decode("utf-8")
        out += response
    if out != '':	
      print(out)
    return out

def write_data(ser,t0,f):
    time.sleep(28)
    result = float(read_pres(ser)[1:])
    tt = time.time()
    t1 = time.time()-t0
    f.write('\n'+str(tt)+','+str(t1)+','+str(result))
        
def timed_read(minutes):
    t0 = time.time()
    t_end = time.time()+minutes*60
    ser = vacconnect()
    f = open(r'C:\Users\sesel\OneDrive - Arizona State University\LASI-Alpha\Documents\mono_vac_data\Mono_vac_data.txt', 'a')
    while time.time() < t_end:
        time.sleep(28)
        result = float(read_pres(ser)[1:])
        tt = time.time()
        t1 = time.time()-t0
        f.write('\n'+str(tt)+','+str(t1)+','+str(result))
        f.flush()
    ser.close()

'''
#auto on code
#00B0UTURBOUDRY6.0E+01
this is to tell the controller to automatically turn on the turbo gauge when the dry 
guage gets to 6.0E+1 Torr, so right away basically.

'''
def read_util(ser):
    ser.write(b'#00B1UTURBO\r\n')
    time.sleep(2)   
   
    out = ''
    # loop which reads out mean and stddev when calculations are finished
    while ser.inWaiting() > 0:
        response = ser.read(1)
        response = response.decode("utf-8")
        out += response
    if out != '':	
      print(out)
    return out