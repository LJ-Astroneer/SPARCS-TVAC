#!/usr/bin/env python
# LASI Lab -- Keithley 6485 Picoammeter Automation
# Author:  Alex Miller <alexdukemiller@gmail.com> 

# Version = 1.0
# Date = '1/28/14'


import serial
import time

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

    #self.ser.open()

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
    # define a timestamp format
    form = '%Y.%m.%d--%H:%M:%S'

    # define a data file
    f = open('Data.txt', 'a')

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
    time.sleep(6)      

    out = ''
    
    # loop which reads out mean and stddev when calculations are finished
    while self.ser.inWaiting() > 0:
        response = self.ser.read(1)
        if response == b'\n':
            out += ','
        else:
            out += response.decode('utf-8')
    if out != '':	
      f.write(str(out)+'\n')
      print(out)


p = Pico()
p.open_connection()
