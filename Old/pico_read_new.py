"""
Created on Mon May  2 12:41:31 2022

@author: Logan Jensen
"""


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
    
  
  def close_connection(self, port='COM9'):
    self.ser.close()    
      
  # reset and calibrate the picoammeter for measurements
  def setup(self):
    self.ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
    print("\n\nDettach current source from picoammeter...")
    input("Press [ENTER] to continue......")    
    self.ser.write(('*RST' + '\r\n').encode())
    self.ser.write(('SENS:CURR:RANG 2e-9' + '\r\n').encode())
    self.ser.write(('SENS:CURR:NPLC 10' + '\r\n').encode()) #60
    self.ser.write(('INIT' + '\r\n').encode())
    self.ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
    self.ser.write(('SYST:ZCOR ON' + '\r\n').encode()) 
    print("\n\nAttach current source to picoammeter...")
    input("Press [ENTER] to continue......")    
    self.ser.write(('SYST:ZCH OFF' + '\r\n').encode())
    self.ser.write(('SYST:AZER ON' + '\r\n').encode())
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

  # function which takes 20 readings, and then records the mean and stddev to 'Data.txt'
  def multi_readings(self):
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
      time.sleep(12)
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

#%% The photodiode noise hunting code
import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np

p = Pico()
p.open_connection()
p.setup()


filename = input('Title of the file? No spaces or .csv\n')
plt.ion()
fig, ax = plt.subplots()
x, y = [],[]
y2=[]
sc = ax.scatter(x,y)
sc2 = ax.scatter(x,y2)
plt.xlim(0,4000)
plt.ylim(-6e-12,2e-11)
plt.legend(['Average','Standard Deviation'])
plt.draw()

avg = []
std = []
times = []
#code repeats for an hour
time_start = datetime.datetime.now()
while (datetime.datetime.now() - time_start).total_seconds() < 3600:
    output = p.multi_readings()
    a = float(output.split(',')[0])
    s = float(output.split(',')[1])
    t = int((datetime.datetime.now() - time_start).total_seconds())
    avg.append(a)
    std.append(s)
    times.append(t)
    x.append(t)
    y.append(a)
    y2.append(s)
    sc.set_offsets(np.c_[x,y])
    sc2.set_offsets(np.c_[x,y2])
    fig.canvas.draw_idle()
    plt.pause(0.1)
plt.ylim(min(y+y2),max(y+y2))
print('done')
#plt.waitforbuttonpress()


rows = zip(times,avg,std)
with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\noise_hunt\\'+filename+'.csv', 'w',newline='') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)  














#%%
'''
Below are all the function calls that you would use to setup the picoammeter and then close it
'''
# p = Pico()
# p.open_connection()
# p.setup()
# p.close_connection()