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
import numpy as np
#%%
'''
Section 1: Defining picoammeter functions and setting up the device.
Modified from pico_read and from Alex Miller's original code.
'''

class Pico(object):
    '''
    Open Connection is the code that sets up the serial port connection
    to the picoammeter.
    '''
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
        if self.ser.isOpen() == True:
            print("Picoammeter Connected")
    '''
    Close connection is needed to ensure the program releases the COM port
    on completion, otherwise the code may not work with COM port in use
    '''    
    def close_connection(self, port='COM9'):
        self.ser.close()
    '''
    Reset and calibrate the picoammeter for measurements
    '''
    def setup(self):
        print("\n\nDettach current source from picoammeter...")
        input("Press [ENTER] to continue......")    
        self.ser.write(('*RST' + '\r\n').encode())
        self.ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
        self.ser.write(('SENS:CURR:RANG 2e-9' + '\r\n').encode())
        self.ser.write(('SENS:CURR:NPLC 6' + '\r\n').encode())
        self.ser.write(('DISP:ENAB OFF' + '\r\n').encode())
        self.ser.write(('INIT' + '\r\n').encode())
        self.ser.write(('DISP:ENAB ON' + '\r\n').encode())
        self.ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
        self.ser.write(('SYST:ZCOR ON' + '\r\n').encode()) 
        print("\n\nAttach current source to picoammeter...")
        input("Press [ENTER] to continue......")    
        self.ser.write(('SYST:ZCH OFF' + '\r\n').encode())
        time.sleep(2)
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
        

    '''
    Multi_readings takes 20 readings, and then records the mean and stddev
    '''
    def multi_readings(self):
      # define a data file
        self.ser.write(('DISP:ENAB OFF' + '\r\n').encode())
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
        self.ser.write(('DISP:ENAB ON' + '\r\n').encode())
        return out #this value can then be parsed with the .split(',') command
#%%
'''
Section 2: This section sets up the monochromator in the best ways I know how
    adapted from mono_control.py. I do not fully understand the Class and .self
    architecture that is used above yet, so if this is rough and ready then 
    so be it.
'''
class Mono(object):
    '''
    Initialization code required by the monochromator itself to work
    '''
    def init(self):
        self.ser.write(b' \r\n') #always start with a space, should return a #, initializes the device
        time.sleep(1)
        self.ser.write(b'X\r\n') #reads current state of variables
        time.sleep(1)
        Mono.read(self)
    
    '''
    Opens the Monochromator serial port
    '''    
    def open_connection(self,port='COM3'):
        self.ser = serial.Serial(
            	port=port,
            	baudrate=9600,
            	parity=serial.PARITY_NONE,
            	stopbits=serial.STOPBITS_ONE,
            	bytesize=serial.EIGHTBITS,
                timeout=5
            )
        if self.ser.isOpen() == True:
            print("Monochromator Connected")
        Mono.init(self)
    '''
    Close command to release the serial port
    '''
    def close_connection(self,port='COM3'):
        self.ser.close()   
    '''
    Read is the command necessary to read the outputs from the monochromator
    scan controller when it is issued a command     
    '''     
    def read(self):
        out = ''
        while self.ser.inWaiting() > 0:
            response = self.ser.read(1)
            response = response.decode("ascii")
            out += response
        if out != '':	
          # print(out)
          return out
    '''
    Write _prompt issues you a prompt to submit any command from the table
    in the McPherson Scan Controller manual
    '''
    def write_prompt(self):
        command = input('Enter desired Command from Table \n')
        full_cmd = str(command)+'\r\n'
        self.ser.write(full_cmd.encode())
        time.sleep(1)
        out = Mono.read(self)
        return out
    '''
    Same as write_prompt but without the prompting call
    '''
    def write(self,command):
        full_cmd = str(command)+'\r\n'
        self.ser.write(full_cmd.encode())
        time.sleep(1)
        out = Mono.read(self)
        return out
    '''
    Command sequence to move the monochromator grating's stepper motor. There are 18000 steps
    per nm and there must be an integer number of steps.
    '''
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
    
    '''
    This is a custom algorithm to sample the dark current of the picoammeter/photodiode
    before performing a spectral scan with light. This does not technically make any
    calls to the monochromator but was esier to put in this class. Data saves to
    the Darks folder with the time.time() result at start as the filename.
    '''
    def dark_scan(self,p,filename):
        print('\nBegin dark current sampling\n')
        input('Ensure Monochromator Lamp, RGA, and any other light source are OFF, then press [ENTER]')
        f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Darks\\'+filename+'_dark.csv', 'a')
        filt=1
        wv = 0
        avg = ['Average Current (A)']
        std = ['Standard Deviation']
        wl = ['Sample #']
        filters = ['Filter used: 1=none, 2=160nm lp, 3=220nm lp, 4=320nm lp']
        while wv <= 5:
            print('Dark Sample '+str(wv))
            output = p.multi_readings()
            time.sleep(1) #readout of the photodiode is sometimes janky
            wl.append(wv)
            avg.append(output.split(',')[0])
            std.append(output.split(',')[1])
            filters.append(filt)
            wv+=1
        rows = zip(wl,avg,std,filters)
        with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Darks\\'+filename+'_dark.csv', 'w',newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)   
        dark_median = np.median(list(map(float,avg[1:])))
        dark_std = np.median(list(map(float,std[1:])))
        print('Dark current sampling complete, saved to Documents\\pico_data\\Darks\\'+filename+'_dark.csv')
        return(dark_median,dark_std)            
    '''
    This is a custom algorithm to use the monochromator and picoammeter in tandem
    to fully sample a custom spectrum of light at custom resolution. Follow the
    prompts and generally it works best if starting wavelength < final wavelength.
  '''
    def wave_scan(self,p):
        filename = str(time.time())
        print('\nBegin full SPARCS spectrum sampling\n')
        input('Turn on Monochromator Lamp, then press [ENTER]')
        time.sleep(10)
        input('Ensure Monochromator filter wheel is set to #1: Empty \nThen Press [Enter]')
        f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Raw\\'+filename+'_raw.csv', 'a')
        current = float(input('Current Wavelength?\n'))
        start = float(input('Starting Wavelegnth?\n'))
        step = float(input('Step?\n'))
        end = float(input('Final Wavelength?\n'))
        #get to starting location
        to_start = (start-current)
        if to_start != 0:
            Mono.move(self,to_start)
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
            print("Starting Wavelength: "+str(start)+"nm  Reached\n")
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
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
            print("Step Complete")
      
        rows = zip(wl,avg,std)
        with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Raw\\'+filename+'_raw.csv', 'w',newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)            
    
    '''
    The Master code for SPARCS operations. This code automatically operates both
    the dark_scan code and a custom wave_scan code to fully sample the SPARCS
    bandpass of interest, which is really the full spectrum of the monochromator
    as built in 2023, 116-550nm. This is the code that will be used most often.
    Saves dark data to the Darks folder, raw data to the Raw folder, and the 
    data with dark current subtration to the Dark_subtracted folder. Follow the prompts
    '''
    def full_scan(self,p):
        filename = str(time.time())
        dark_median,dark_std = Mono.dark_scan(self,p,filename)
        print('\nBegin full SPARCS spectrum sampling\n')
        input('Turn on Monochromator Lamp, then press [ENTER]')
        time.sleep(10)
        b = int(input('FUV (1) or NUV (2) sampling? Type 1 or 2\n'))
        input('Ensure Monochromator filter wheel is set to #1: Empty \nThen Press [Enter]')
        current = float(input('Current Wavelength? HOME = 261.81\n'))
        start = 110.0
        step = 5
        end = 550.0
        filt = 1
        #get to starting location
        to_start = (start-current)
        if to_start != 0:
            Mono.move(self,to_start)
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
            print("Starting Wavelength: "+str(start)+"nm  Reached\n")
        #loop through the steps
        wv = start
        avg = 'Average Current (A)'
        std = 'Standard Deviation'
        sub = 'Dark Substracted Average'
        if b == 1:    
            wl = 'Wavelength (nm) FUV Band'
            f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\FUV\\'+filename+'.csv', 'a')
        if b ==2:
            wl = 'Wavelength (nm) NUV Band'
            f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\NUV\\'+filename+'.csv', 'a')
        filters = 'Filter used: 1=none 2=160nm lp 3=220nm lp 4=320nm lp'
        f.write('\n'+wl+','+avg+','+std+','+sub+','+filters)
        while wv < 160:
            print('Reading at {:.2f}'.format(wv))
            output = p.multi_readings()
            time.sleep(1) #readout of the photodiode is sometimes janky
            wl = wv
            avg = output.split(',')[0]
            std = output.split(',')[1]
            sub = float(avg) - dark_median
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            if b == 1:
                if wv >= 118 and wv <= 206:
                    step = 1
                else:
                    step = 5
            if b == 2:
                if wv >= 200 and wv <= 360:
                    step = 1
                else:
                    step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        input('Change Monochromator filter to #2, then press [ENTER]')
        filt = 2
        while wv < 300:
            print('Reading at {:.2f}'.format(wv))
            output = p.multi_readings()
            time.sleep(1) #readout of the photodiode is sometimes janky
            wl = wv
            avg = output.split(',')[0]
            std = output.split(',')[1]
            sub = float(avg) - dark_median
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            if b == 1:
                if wv >= 118 and wv <= 206:
                    step = 1
                else:
                    step = 5
            if b == 2:
                if wv >= 200 and wv <= 360:
                    step = 1
                else:
                    step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        input('Change Monochromator filter to #3, then press [ENTER]')
        filt = 3 
        while wv < 400:
            print('Reading at {:.2f}'.format(wv))
            output = p.multi_readings()
            time.sleep(1) #readout of the photodiode is sometimes janky
            wl = wv
            avg = output.split(',')[0]
            std = output.split(',')[1]
            sub = float(avg) - dark_median
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            if b == 1:
                if wv >= 118 and wv <= 206:
                    step = 1
                else:
                    step = 5
            if b == 2:
                if wv >= 200 and wv <= 360:
                    step = 1
                else:
                    step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)  
        input('Change Monochromator filter to #4, then press [ENTER]')
        filt = 4
        while wv <= end:
            print('Reading at {:.2f}'.format(wv))
            output = p.multi_readings()
            time.sleep(1) #readout of the photodiode is sometimes janky
            wl = wv
            avg = output.split(',')[0]
            std = output.split(',')[1]
            sub = float(avg) - dark_median
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            if b == 1:
                if wv >= 118 and wv <= 206:
                    step = 1
                else:
                    step = 5
            if b == 2:
                if wv >= 200 and wv <= 360:
                    step = 1
                else:
                    step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)   
        f.close()
        print('Scan Complete')

    '''
    Small test script to move the monochroamtor specific wavelength distances
    '''            
    def test(self):
        step = float(input('Move how Far (nm)?\n'))
        Mono.move(self,step)
        while Mono.write(self,'^') != '^   0 \r\n':
            time.sleep(1)
        print("Move Complete")
#%% Everything in this block auto executes the above functions to perform the
#whole process needed by SPARCS for sampling
'''
Section 3: Setting up the connections and picoammeter.
'''
def setup():
    p = Pico()
    p.open_connection() #opens port
    p.setup() #zeros the system
    m = Mono()
    m.open_connection()
    return p,m

'''
Section 4: The Execution block
'''
p,m = setup()
m.full_scan(p)
m.close_connection()
p.close_connection()

'''
re-write the saving section to write the data as separate columns but in the same file
then use the .flush command to make sure the data is being saved during the loop
otherise stopping the code results in all the data being lost.
'''