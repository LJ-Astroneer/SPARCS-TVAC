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
import datetime
import matplotlib.pyplot as plt

'''
Section 1: Defining picoammeter functions and setting up the device.
Modified from pico_read and from Alex Miller's original code.
'''

class Pico(object):
    def setup():
        ser = serial.Serial(
            port='COM9',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=None)
        ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
        print("\n\nDettach current source from picoammeter...")
        input("Press [ENTER] to continue......")    
        ser.write(('*RST' + '\r\n').encode())
        ser.write(('SENS:CURR:RANG 2e-9' + '\r\n').encode())
        ser.write(('SENS:CURR:NPLC 10' + '\r\n').encode()) #60
        ser.write(('INIT' + '\r\n').encode())
        ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
        ser.write(('SYST:ZCOR ON' + '\r\n').encode()) 
        print("\n\nAttach current source to picoammeter...")
        input("Press [ENTER] to continue......")    
        ser.write(('SYST:ZCH OFF' + '\r\n').encode())
        ser.write(('SYST:AZER ON' + '\r\n').encode())
        return(ser)

    def read(ser):
        ser.write(('FORM:ELEM READ' + '\r\n').encode())
        ser.write(('ARM:SOUR IMM' + '\r\n').encode())
        ser.write(('TRIG:COUN 20' + '\r\n').encode())
        ser.write(('TRAC:POIN 20' + '\r\n').encode())
        ser.write(('TRAC:FEED SENS' + '\r\n').encode())
        ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode())
        ser.write(('INIT' + '\r\n').encode())
        ser.write(('TRAC:DATA?' + '\r\n').encode())
        out = ''
        response = ser.readline()
        out = response.decode('utf-8')
        out = (out.strip('\n')).split(',')
        out = [float(i) for i in out]
        return out
    
    def close_connection(ser):
        ser.close()    


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
    def dark_scan(self,ser,filename):
        print('\nBegin dark current sampling\n')
        input('Ensure Monochromator Lamp, RGA, and any other light source are OFF, then press [ENTER]')
        wv = 0
        reads = []
        avg = []
        wl = []
        while wv <= 5:
            print('Dark Sample '+str(wv))
            output = Pico.read(ser)
            wl.append(wv)
            reads.append(output)
            avg.append(np.mean(reads))
            print(np.mean(reads))
            wv+=1
        rows = zip(wl,reads)
        with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Darks\\'+filename+'_dark.csv', 'w',newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)   
        dark_avg = np.mean(reads)
        count = sum([len(i) for i in reads])
        dark_std = np.std(reads)/np.sqrt(count)
        print('Dark current sampling complete, saved to Documents\\pico_data\\Darks\\'+filename+'_dark.csv')
        return(dark_avg,dark_std)            
    
    '''
    The Master code for SPARCS operations. This code automatically operates both
    the dark_scan code and a custom wave_scan code to fully sample the SPARCS
    bandpass of interest, which is really the full spectrum of the monochromator
    as built in 2023, 116-550nm. This is the code that will be used most often.
    Saves dark data to the Darks folder, raw data to the Raw folder, and the 
    data with dark current subtration to the Dark_subtracted folder. Follow the prompts
    '''
    def full_scan(self,ser):
        filename = input('Filename for data, no spaces\n')
        dark_avg,dark_std = Mono.dark_scan(self,ser,filename)
        print('\nBegin full SPARCS spectrum sampling\n')
        input('Turn on Monochromator Lamp, then press [ENTER]')
        b = int(input('FUV (1) or NUV (2) sampling? Type 1 or 2\n'))
        input('Ensure Monochromator filter wheel is set to #1: Empty \nThen Press [Enter]')
        current = float(input('Current Wavelength? HOME = 261.81\n'))
        start = 110.0
        step = 10
        end = 550.0
        filt = 1
        #get to starting location
        to_start = (start-current)
        if to_start != 0:
            Mono.move(self,to_start)
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
            print("Starting Wavelength: "+str(start)+"nm  Reached\n")
        
        #Setup the plot
        plt.ion()
        fig, ax = plt.subplots()
        x, y = [],[]
        y2=[]
        sc = ax.scatter(x,y)
        sc2 = ax.scatter(x,y2)
        plt.xlim(0,600)
        plt.ylim(-6e-12,9e-11)
        plt.legend(['Average','Standard Deviation'])
        plt.draw()
        
        #setup the data
        wv = start
        avg = 'Average Current (A)'
        std = 'Standard Deviation'
        sub = 'Dark Substracted, median dark = {:.2e}, std:{:.2e}'.format(dark_avg,dark_std)
        filters = 'Filter used: 1=none 2=160nm lp 3=220nm lp 4=320nm lp'
        reads=[]
        #choose the NUV or FUV sampling
        if b == 1:    
            wl = 'Wavelength (nm) FUV Band'
            f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\FUV\\'+filename+'.csv', 'a')
        if b ==2:
            wl = 'Wavelength (nm) NUV Band'
            f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\NUV\\'+filename+'.csv', 'a')
        f.write('\n'+wl+','+avg+','+std+','+sub+','+filters)
        while wv < 160:
            print('Reading at {:.2f}'.format(wv))
            output = Pico.read(ser)
            wl = wv
            reads.append(output)
            avg = np.mean(output)
            std = np.std(output)/np.sqrt(len(output))
            sub = avg - dark_avg
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(avg)
            y2.append(std)
            sc.set_offsets(np.c_[x,y])
            sc2.set_offsets(np.c_[x,y2])
            fig.canvas.draw_idle()
            plt.pause(0.1)
            
            # if b == 1:
            #     if wv >= 107 and wv <= 203:
            #         step = 1
            #     else:
            #         step = 5
            # if b == 2:
            #     if wv >= 188 and wv <= 372:
            #         step = 1
            #     else:
            #         step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        input('Change Monochromator filter to #2, then press [ENTER]')
        filt = 2
        while wv < 300:
            print('Reading at {:.2f}'.format(wv))
            output = Pico.read(ser)
            wl = wv
            reads.append(output)
            avg = np.mean(output)
            std = np.std(output)/np.sqrt(len(output))
            sub = avg - dark_avg
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(avg)
            y2.append(std)
            sc.set_offsets(np.c_[x,y])
            sc2.set_offsets(np.c_[x,y2])
            fig.canvas.draw_idle()
            plt.pause(0.1)
            
            # if b == 1:
            #     if wv >= 107 and wv <= 203:
            #         step = 1
            #     else:
            #         step = 5
            # if b == 2:
            #     if wv >= 188 and wv <= 372:
            #         step = 1
            #     else:
            #         step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        input('Change Monochromator filter to #3, then press [ENTER]')
        filt = 3 
        while wv < 400:
            print('Reading at {:.2f}'.format(wv))
            output = Pico.read(ser)
            wl = wv
            reads.append(output)
            avg = np.mean(output)
            std = np.std(output)/np.sqrt(len(output))
            sub = avg - dark_avg
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(avg)
            y2.append(std)
            sc.set_offsets(np.c_[x,y])
            sc2.set_offsets(np.c_[x,y2])
            fig.canvas.draw_idle()
            plt.pause(0.1)
            
            # if b == 1:
            #     if wv >= 107 and wv <= 203:
            #         step = 1
            #     else:
            #         step = 5
            # if b == 2:
            #     if wv >= 188 and wv <= 372:
            #         step = 1
            #     else:
            #         step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        input('Change Monochromator filter to #4, then press [ENTER]')
        filt = 4
        while wv <= end:
            print('Reading at {:.2f}'.format(wv))
            output = Pico.read(ser)
            wl = wv
            reads.append(output)
            avg = np.mean(output)
            std = np.std(output)/np.sqrt(len(output))
            sub = avg - dark_avg
            filters = filt
            f.write('\n'+str(wl)+','+str(avg)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(avg)
            y2.append(std)
            sc.set_offsets(np.c_[x,y])
            sc2.set_offsets(np.c_[x,y2])
            fig.canvas.draw_idle()
            plt.pause(0.1)
            
            # if b == 1:
            #     if wv >= 107 and wv <= 203:
            #         step = 1
            #     else:
            #         step = 5
            # if b == 2:
            #     if wv >= 188 and wv <= 372:
            #         step = 1
            #     else:
            #         step = 5
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        plt.ylim(min(y+y2),max(y+y2))
        f.close()
        rows = zip(x,reads)
        with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Raw\\'+filename+'_dark.csv', 'w',newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row) 
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

'''
Section 3: Setting up the connections and picoammeter.
'''
def setup():
    ser = Pico.setup()
    m = Mono()
    m.open_connection()
    return ser,m
#%% Everything in this block auto executes the above functions to perform the
#whole process needed by SPARCS for sampling
'''
Section 4: The Execution block
'''
ser,m = setup()
m.full_scan(ser)
m.close_connection()
Pico.close_connection()

'''
re-write the saving section to write the data as separate columns but in the same file
then use the .flush command to make sure the data is being saved during the loop
otherise stopping the code results in all the data being lost.
'''