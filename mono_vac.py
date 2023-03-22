# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 15:59:41 2022

@author: Logan Jensen
"""
import time
import serial
import datetime

class Pump(object):
    # configure the serial connections (the parameters differs on the device you are connecting to)
    def vacconnect(self,port='COM10'):
        self.ser = serial.Serial(
        	port=port,
        	baudrate=9600,
        	parity=serial.PARITY_NONE,
        	stopbits=serial.STOPBITS_ONE,
        	bytesize=serial.EIGHTBITS,
            timeout=5)
        if self.ser.isOpen() == True:
            print("Pump controller Connected")
    
    def close_connection(self,port='COM10'):
        self.ser.close()
        
    def read_pres(self):
        self.ser.write(b'#0002UTURBO\r\n')
        time.sleep(1)   
       
        out = ''
        # loop which reads out mean and stddev when calculations are finished
        while self.ser.inWaiting() > 0:
            response = self.ser.read(2)
            response = response.decode("utf-8")
            out += response
        if out != '':	
          print(out)
        return out
    
    def read_dry(self):
        self.ser.write(b'#0002UDRY\r\n')
        time.sleep(2)   
       
        out = ''
        # loop which reads out mean and stddev when calculations are finished
        while self.ser.inWaiting() > 0:
            response = self.ser.read(1)
            response = response.decode("utf-8")
            out += response
        if out != '':	
          print(out)
        return out
    
    def write_data(self,t0,f):
        time.sleep(28)
        result = float(Pump.read_pres(self)[1:])
        tt = time.time()
        t1 = time.time()-t0
        f.write('\n'+str(tt)+','+str(t1)+','+str(result))
            
    def timed_read(self,hours):
        filename = str(time.time())
        t_end = time.time()+(float(hours)*60*60)
        # self.ser = vacconnect()
        f = open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\mono_vac_data\\'+filename+'.csv', 'a')
        f.write('Time.time(),Pressure(Torr)')
        while time.time() < t_end:
            time.sleep(5)
            result = float(Pump.read_pres(self)[1:])
            tt = time.time()
            f.write('\n'+str(tt)+','+str(result))
            f.flush()
        f.close()
    '''
    #auto on code
    #00B0UTURBOUDRY6.0E+01
    this is to tell the controller to automatically turn on the turbo gauge when the dry 
    guage gets to 6.0E+1 Torr, so right away basically.
    
    '''
    def read_util(self):
        self.ser.write(b'#00B1UTURBO\r\n')
        time.sleep(2)   
       
        out = ''
        # loop which reads out mean and stddev when calculations are finished
        while self.ser.inWaiting() > 0:
            response = self.ser.read(1)
            response = response.decode("utf-8")
            out += response
        if out != '':	
          print(out)
        return out
#%%
v = Pump()
v.vacconnect()
hours = input('How many hours of data?')
v.timed_read(hours)
v.close_connection()


