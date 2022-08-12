# -*- coding: utf-8 -*-
"""
Created on Tue May 10 11:13:00 2022

@author: Logan Jensen

This code is used to perform a scan across wavelength bandpasses using the 
Mcpherson UV monohcromator and the NIST photodiode and picoammeter. Code has 
been pulled from "pico_read.py" for the picoammeter control and "mono_control.py"
for the monochromator control. 
NOTE: you need neither of those codes to run this, it is all here.
Monochromator home wv is 261.81 nm
"""

import serial
import time
import csv
#%%
'''
Section 1: Defining picoammeter functions and setting up the device.
Modified from pico_read and from Alex Miller's original code.

Goal: Adjust the functions to return data from the pico rather than printing
        it straight to a file. This will make it easy to create a better file
        later which includes wavelength values
'''

class Pico(object):

    def open_connection(self, port='COM9'):  
        # configure the serial connections
        self.ser = serial.Serial(
          port=port,
          baudrate=9600,
          bytesize=serial.EIGHTBITS,
          parity=serial.PARITY_NONE,
          stopbits=serial.STOPBITS_ONE,
          timeout=0.1)   
        self.ser.readlines()

  # reset and calibrate the picoammeter for measurements
    def setup(self):
        self.ser.write(('*RST' + '\r\n').encode())
        self.ser.write((':SYST:ZCH ON' + '\r\n').encode()) 
        self.ser.write((':SENS:CURR:RANG 2e-9' + '\r\n').encode())  
        self.ser.write((':SYST:ZCOR ON' + '\r\n').encode()) 
        self.ser.write((':SENS:CURR:RANG:AUTO ON' + '\r\n').encode()) 
          
        print("\n\nAttach current source to picoammeter...\n\n")
        
        input("Press [ENTER] to continue......")    
          
        self.ser.write((':SYST:ZCH OFF' + '\r\n').encode())
        self.ser.write((':SENS:CURR:NPLC 2' + '\r\n').encode())

    # function which takes 20 readings, and then records the mean and stddev to 'Data.txt'
    def multi_readings(self):
      # define a data file
        self.ser.write(('FORM:ELEM READ,TIME' + '\r\n').encode())
        self.ser.write(('ARM:SOUR IMM' + '\r\n').encode())
        self.ser.write(('TRIG:COUN 20' + '\r\n').encode())
        self.ser.write(('TRAC:POIN 20' + '\r\n').encode())
        self.ser.write(('TRAC:FEED SENS' + '\r\n').encode())
        self.ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode())
        self.ser.write(('INIT' + '\r\n').encode())
        self.ser.write(('CALC3:FORM MEAN' + '\r\n').encode())
        self.ser.write(('CALC3:DATA?' + '\r\n').encode())
        self.ser.write(('CALC3:FORM SDEV' + '\r\n').encode())
        self.ser.write(('CALC3:DATA?' + '\r\n').encode())  
        time.sleep(10)      
          
        out = ''
      
      # loop which reads out mean and stddev when calculations are finished
        while self.ser.inWaiting() > 0:
            response = self.ser.read(1)
            if response == b'\n':
                out += ','
            else:
                out += response.decode('utf-8')
        if out != '':	
          print(out)
        return out #this value can then be parsed with the .split(',') command

#%%
'''
Section 2: This section sets up the monochromator in the best ways I know how
    adapted from mono_control.py. I do not fully understand the Class and .self
    architecture that is used above yet, so for now these are base functions
'''
class Mono(object):
    def init(self):
        self.ser.write(b' \r\n') #always start with a space, should return a #, initializes the device
        time.sleep(1)
        self.ser.write(b'X\r\n') #reads current state of variables
        time.sleep(1)
        Mono.read(self)
        
    def open_connection(self,port='COM3'):
        self.ser = serial.Serial(
            	port=port,
            	baudrate=9600,
            	parity=serial.PARITY_NONE,
            	stopbits=serial.STOPBITS_ONE,
            	bytesize=serial.EIGHTBITS,
                timeout=5
            )
        print(self.ser.isOpen())
        Mono.init(self)
        
    def read(self):
        out = ''
        while self.ser.inWaiting() > 0:
            response = self.ser.read(1)
            response = response.decode("ascii")
            out += response
        if out != '':	
          print(out)
    
    def write(self):
        command = input('Enter desired Command from Table \n')
        full_cmd = str(command)+'\r\n'
        self.ser.write(full_cmd.encode())
        time.sleep(1)
        Mono.read(self)
        
    def move(self,nm):
        steps = int(nm*18000)
        if steps < 0:
            command = str(steps)+'\r\n'
            #print(command.encode())
            self.ser.write(command.encode())
        else:
            command = '+'+str(steps)+'\r\n'
            #print(command.encode())
            self.ser.write(command.encode())     

    def wave_scan(self,p):
        #p = Pico()
        #p.open_connection()
        #p.setup()
        input('Turn on Monochromator Lamp, then press [ENTER]')
        f = open(r'C:\Users\sesel\OneDrive - Arizona State University\LASI-Alpha\Documents\pico_data\pico_data.txt', 'a')
        current = float(input('Current Wavelength?\n'))
        start = float(input('Starting Wavelegnth?\n'))
        step = float(input('Step?\n'))
        end = float(input('Final Wavelength?\n'))
        if end < start:
            step = step*-1
        
        #get to starting location
        to_start = int((start-current))
        if to_start != 0:
            Mono.move(self,to_start)
            if to_start < 30:
                time.sleep(abs(to_start*1.5))
            else:
                time.sleep(abs(to_start*0.3))
        #loop through the steps
        wv = start
        avg = ['Average Current (A)']
        std = ['Standard Deviation']
        wl = ['Wavelength (nm)']
        while wv <= end:
            print('Reading at {:.2f}'.format(wv))
            output = p.multi_readings()
            time.sleep(1) #readout of the photodiode is sometimes janky
            wl.append(wv)
            avg.append(output.split(',')[0])
            std.append(output.split(',')[1])
            Mono.move(self,step)
            wv+=step
            time.sleep(1.5*abs(step)) #small steps are slow on the mono
        rows = zip(wl,avg,std)
        with open(r'C:\Users\sesel\OneDrive - Arizona State University\LASI-Alpha\Documents\pico_data\pico_data.csv', 'w',newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
    def test(self):
        step = float(input('Step?\n'))
        Mono.move(self,step)
#%%
'''
Section 3: What you need to do to get the wave scan running.
'''
# actually sets up the picoammeter, should have photodiode disconnected for zeroing
# from wavelength_scan import Mono,Pico 
# p = Pico()
# p.open_connection() #opens port
# p.setup() #zeros the system
# m = Mono()
# m.open_connection()
# m.wave_scan()


#%%
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
#     p.multi_readings()
#     time.sleep(7) #readout of the photodiode takes about 6.1 seconds, 7 for margin
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
