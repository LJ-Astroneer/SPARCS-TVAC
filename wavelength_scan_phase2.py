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
        ser.write(('*RST' + '\r\n').encode())
        ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
        print("\n\nDettach current source from picoammeter...")
        input("Press [ENTER] to continue......")    
        ser.write(('DISP:ENAB OFF' + '\r\n').encode())
        ser.write(('RANG 2e-9' + '\r\n').encode())
        ser.write(('SENS:CURR:NPLC 6' + '\r\n').encode()) #exp 10 May DCJ
        ser.write(('INIT' + '\r\n').encode())
        ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
        ser.write(('SYST:ZCOR ON' + '\r\n').encode())
        ser.write(('RANG:AUTO ON' + '\r\n').encode())
        ser.write(('SYST:AZER ON' + '\r\n').encode())
        print("\n\nAttach current source to picoammeter...")
        input("Press [ENTER] to continue......")    
        ser.write(('SYST:ZCH OFF' + '\r\n').encode())
        ser.write(('DISP:ENAB ON' + '\r\n').encode())
        return(ser)

    def read(ser):
        #after pg 102 of manual "1000 readings/second into internal buffer
        ser.write(('DISP:ENAB OFF' + '\r\n').encode())
        ser.write(('*CLS' + '\r\n').encode())
        ser.write(('FORM:ELEM READ' + '\r\n').encode())
        ser.write(('TRIG:COUN 50' + '\r\n').encode())  #exp 10 May  DCJ
        ser.write(('TRAC:POIN 50' + '\r\n').encode())  #exp 10 May DCJ
        ser.write(('TRAC:CLE'+'\r\n').encode()) #clear buffer
        ser.write(('TRAC:FEED SENS' + '\r\n').encode())
        ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode()) #set storage control to start on next reading
        ser.write(('STAT:MEAS:ENAB 512' + '\r\n').encode()) #enable buffer full measurement event
        ser.write(('*SRE 1' + '\r\n').encode()) #enable SRQ on buffer full measurement event
        #here the example does a *OPC? and then waits on the result. We are not doing this yet. Is it important?!?
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
        med = []
        wl = []
        while wv <= 10:
            print('Dark Sample '+str(wv))
            output = Pico.read(ser)
            wl.append(wv)
            reads.append(output)
            med.append(np.median(output))
            print("Median = {:.2e} Std.Dev = {:.2e}".format(np.median(output),np.std(output)))
            wv+=1
        rows = zip(wl,reads)
        with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Darks\\'+filename+'_dark.csv', 'w',newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)   
        dark_med = np.median(reads)
        count = sum([len(i) for i in reads])
        dark_std = np.std(reads)#/np.sqrt(count)
        print('Dark current sampling complete, saved to Documents\\pico_data\\Darks\\'+filename+'_dark.csv')
        return(dark_med,dark_std)            
    
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
        dark_med,dark_std = Mono.dark_scan(self,ser,filename)
        print('\nBegin full SPARCS spectrum sampling\n')
        input('Turn on Monochromator Lamp, then press [ENTER]')
        b = int(1)#int(input('FUV (1) or NUV (2) sampling? Type 1 or 2\n'))
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
        plt.ion()
        fig = plt.figure()
        fig.set_figheight(7)
        fig.set_figwidth(10)
        graph1 = fig.add_subplot(221)
        graph2 = fig.add_subplot(222)
        graph3 = fig.add_subplot(223)
        graph4 = fig.add_subplot(224)
        
        x, y = [],[]
        y2=[]
        def graph(x,y,y2,reads,dark_med):
            graph1.clear()
            graph2.clear()
            graph3.clear()
            graph4.clear()
            graph1.axhline(y=dark_med,color='r', linestyle='-')
            graph2.axhline(y=dark_med,color='r', linestyle='-')
            graph3.axhline(y=dark_med,color='r', linestyle='-')
            graph4.axhline(y=dark_med,color='r', linestyle='-')
            graph1.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
            graph1.set_title('Median w/ Std.dev Error')
            graph2.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
            graph2.set_title('Median w/ Std.dev Error (log)')
            graph2.set_yscale('log')
            graph3.plot(reads)
            graph3.set_title('Raw data')
            graph4.plot(reads)
            graph4.set_title('Raw data (log)')
            graph4.set_yscale('log')
            fig.canvas.draw()
            fig.canvas.flush_events()
        reads=[]
        graph(x,y,y2,reads,dark_med)
        
        #setup the data
        wv = start
        raw = 'Raw Data (A)'
        med = 'Median Current (A)'
        std = 'Standard Deviation'
        sub = 'Dark Substracted, median dark = {:.2e}, std:{:.2e}'.format(dark_med,dark_std)
        filters = 'Filter used: 1=none 2=160nm lp 3=220nm lp 4=320nm lp'
        reads=[]
        wl = 'Wavelength (nm) FUV Band'
        f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Phase2\\'+filename+'.csv', 'a')
        f.write('\n'+wl+','+raw+','+med+','+std+','+sub+','+filters)
        while wv < 160:
            print('Reading at {:.2f}'.format(wv))
            output = Pico.read(ser)
            wl = wv
            reads.append(output)
            raw=output
            med = np.median(output)
            std = np.std(output)#/np.sqrt(len(output))
            sub = med - dark_med
            filters = filt
            f.write('\n'+str(wl)+','+str(raw)+','+str(med)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(med)
            y2.append(std)
            graph(x,y,y2,reads,dark_med)
            print("Median = {:.2e} Std.Dev = {:.2e} SNR = {:.2f}".format(y[-1],y2[-1],y[-1]/y2[-1]))
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        input('Change Monochromator filter to #2, then press [ENTER]')
        filt = 2
        while wv < 280:
            print('Reading at {:.2f}'.format(wv))
            output = Pico.read(ser)
            wl = wv
            reads.append(output)
            raw=output
            med = np.median(output)
            std = np.std(output)#/np.sqrt(len(output))
            sub = med - dark_med
            filters = filt
            f.write('\n'+str(wl)+','+str(raw)+','+str(med)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(med)
            y2.append(std)
            graph(x,y,y2,reads,dark_med)
            plt.pause(0.1)
            print("Median = {:.2e} Std.Dev = {:.2e} SNR = {:.2f}".format(y[-1],y2[-1],y[-1]/y2[-1]))
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
            raw=output
            med = np.median(output)
            std = np.std(output)#/np.sqrt(len(output))
            sub = med - dark_med
            filters = filt
            f.write('\n'+str(wl)+','+str(raw)+','+str(med)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(med)
            y2.append(std)
            graph(x,y,y2,reads,dark_med)
            plt.pause(0.1)
            print("Median = {:.2e} Std.Dev = {:.2e} SNR = {:.2f}".format(y[-1],y2[-1],y[-1]/y2[-1]))
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
            raw=output
            med = np.median(output)
            std = np.std(output)#/np.sqrt(len(output))
            sub = med - dark_med
            filters = filt
            f.write('\n'+str(wl)+','+str(raw)+','+str(med)+','+str(std)+','+str(sub)+','+str(filters))
            f.flush()
            
            x.append(wv)
            y.append(med)
            y2.append(std)
            graph(x,y,y2,reads,dark_med)
            plt.pause(0.1)
            print("Median = {:.2e} Std.Dev = {:.2e} SNR = {:.2f}".format(y[-1],y2[-1],y[-1]/y2[-1]))
            Mono.move(self,step)
            wv+=step
            while Mono.write(self,'^') != '^   0 \r\n':
                time.sleep(1)
        plt.figure()
        plt.scatter(x,y)
        plt.errorbar(x,y,xerr=step/2,yerr=y2,fmt='o')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Median Current (Amp)')
        plt.title('Current versus wavelength with error')
        f.close()
        rows = zip(x,reads)
        with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\Raw\\'+filename+'.csv', 'w',newline='') as f:
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
Pico.close_connection(ser)

'''
'''