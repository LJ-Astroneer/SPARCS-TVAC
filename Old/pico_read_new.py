"""
Created on Mon May  2 12:41:31 2022

@author: Logan Jensen
"""

import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import serial
import time

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
        ser.write(('DISP:ENAB OFF' + '\r\n').encode())
        ser.write(('RANG 2e-9' + '\r\n').encode())
        ser.write(('SENS:CURR:NPLC 6' + '\r\n').encode()) #exp 10 May DCJ
        ser.write(('INIT' + '\r\n').encode())
        time.sleep(1)
        print("\n\nDettach current source from picoammeter...")
        input("Press [ENTER] to continue......")    
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
        ser.write(('TRIG:COUN 100' + '\r\n').encode())  #exp 10 May  DCJ
        ser.write(('TRAC:POIN 100' + '\r\n').encode())  #exp 10 May DCJ
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
        return out,response
    
    def close_connection(ser):
        ser.close()    

class Mono(object):
    def sample(ser):
        data = Pico.read(ser)
        return data
    #%%
    
    # def open_connection(self, port='COM9'):  
    
    #   # configure the serial connections
    #   self.ser = serial.Serial(
    #     port=port,
    #     baudrate=9600,
    #     bytesize=serial.EIGHTBITS,
    #     parity=serial.PARITY_NONE,
    #     stopbits=serial.STOPBITS_ONE,
    #     timeout=1)
    
    #   #self.ser.open()
    #   self.ser.readlines()
      
    
    # def close_connection(self, port='COM9'):
    #   self.ser.close()    
        
    # # reset and calibrate the picoammeter for measurements
    # def setup(self):
    #   self.ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
    #   print("\n\nDettach current source from picoammeter...")
    #   input("Press [ENTER] to continue......")    
    #   self.ser.write(('*RST' + '\r\n').encode())
    #   self.ser.write(('SENS:CURR:RANG 2e-9' + '\r\n').encode())
    #   self.ser.write(('SENS:CURR:NPLC 10' + '\r\n').encode()) #60
    #   self.ser.write(('INIT' + '\r\n').encode())
    #   self.ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
    #   self.ser.write(('SYST:ZCOR ON' + '\r\n').encode()) 
    #   print("\n\nAttach current source to picoammeter...")
    #   input("Press [ENTER] to continue......")    
    #   self.ser.write(('SYST:ZCH OFF' + '\r\n').encode())
    #   self.ser.write(('SYST:AZER ON' + '\r\n').encode())
    #   time.sleep(2)
    #   out = ''
    # # loop which reads out mean and stddev when calculations are finished
    #   while self.ser.inWaiting() > 0:
    #       response = self.ser.read(1)
    #       if response == b'\n':
    #           out += ','
    #       else:
    #           out += response.decode('utf-8')
    #   if out != '':	
    #     print(out)
    
    # # function which takes 20 readings, and then records the mean and stddev to 'Data.txt'
    # def multi_readings(self):
    #     self.ser.write(('FORM:ELEM READ,TIME' + '\r\n').encode())
    #     self.ser.write(('ARM:SOUR IMM' + '\r\n').encode())
    #     self.ser.write(('TRIG:COUN 20' + '\r\n').encode())
    #     self.ser.write(('TRAC:POIN 20' + '\r\n').encode())
    #     self.ser.write(('TRAC:FEED SENS' + '\r\n').encode())
    #     self.ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode())
    #     self.ser.write(('INIT' + '\r\n').encode())
    #     self.ser.write(('CALC3:FORM MEAN' + '\r\n').encode())
    #     self.ser.write(('CALC3:DATA?' + '\r\n').encode())
    #     self.ser.write(('CALC3:FORM SDEV' + '\r\n').encode())
    #     self.ser.write(('CALC3:DATA?' + '\r\n').encode())  
    #     time.sleep(12)
    #     out = ''
    #   # loop which reads out mean and stddev when calculations are finished
    #     while self.ser.inWaiting() > 0:
    #         response = self.ser.read(1)
    #         if response == b'\n':
    #             out += ','
    #         else:
    #             out += response.decode('utf-8')
    #     if out != '':	
    #       print(out)
    #     return out #this value can then be parsed with the .split(',') command
    # def raw_readings(self):
    #     self.ser.write(('FORM:ELEM READ' + '\r\n').encode())
    #     self.ser.write(('ARM:SOUR IMM' + '\r\n').encode())
    #     self.ser.write(('TRIG:COUN 20' + '\r\n').encode())
    #     self.ser.write(('TRAC:POIN 20' + '\r\n').encode())
    #     self.ser.write(('TRAC:FEED SENS' + '\r\n').encode())
    #     self.ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode())
    #     self.ser.write(('INIT' + '\r\n').encode())
    #     self.ser.write(('*OPC?' + '\r\n').encode())
    #     self.ser.write(('TRAC:DATA?' + '\r\n').encode())
    #     out = ''
    #   # loop which reads out mean and stddev when calculations are finished
    #     while self.ser.inWaiting() > 0:
    #         response = self.ser.read(1)
    #         if response == b'\n':
    #             out += ','
    #         else:
    #             out += response.decode('utf-8')
    #     if out != '':	
    #       print(out)
    #     return out #this value can then be parsed with the .split(',') command
    # def raw(self):
    #     self.ser = serial.Serial(
    #         port='COM9',
    #         baudrate=9600,
    #         bytesize=serial.EIGHTBITS,
    #         parity=serial.PARITY_NONE,
    #         stopbits=serial.STOPBITS_ONE,
    #         timeout=None)
    #     self.ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
    #     print("\n\nDettach current source from picoammeter...")
    #     input("Press [ENTER] to continue......")    
    #     self.ser.write(('*RST' + '\r\n').encode())
    #     self.ser.write(('SENS:CURR:RANG 2e-9' + '\r\n').encode())
    #     self.ser.write(('SENS:CURR:NPLC 10' + '\r\n').encode()) #60
    #     self.ser.write(('INIT' + '\r\n').encode())
    #     self.ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
    #     self.ser.write(('SYST:ZCOR ON' + '\r\n').encode()) 
    #     print("\n\nAttach current source to picoammeter...")
    #     input("Press [ENTER] to continue......")    
    #     self.ser.write(('SYST:ZCH OFF' + '\r\n').encode())
    #     self.ser.write(('SYST:AZER ON' + '\r\n').encode())
        
    #     self.ser.write(('FORM:ELEM READ' + '\r\n').encode())
    #     self.ser.write(('ARM:SOUR IMM' + '\r\n').encode())
    #     self.ser.write(('TRIG:COUN 20' + '\r\n').encode())
    #     self.ser.write(('TRAC:POIN 20' + '\r\n').encode())
    #     self.ser.write(('TRAC:FEED SENS' + '\r\n').encode())
    #     self.ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode())
    #     self.ser.write(('INIT' + '\r\n').encode())
    #     self.ser.write(('TRAC:DATA?' + '\r\n').encode())
    #     out = ''
    #     response = self.ser.readline()
    #     self.ser.close()
    #     out = response.decode('utf-8')
    #     out = (out.strip('\n')).split(',')
    #     out = [float(i) for i in out]
    #     return out
#%%
# ser = Pico.setup()
# data = Pico.read(ser)
# Pico.close_connection(ser)

       
#%% The photodiode noise hunting code


# p = Pico()
# p.open_connection()
# p.setup()


# filename = input('Title of the file? No spaces or .csv\n')
# plt.ion()
# fig, ax = plt.subplots()
# x, y = [],[]
# y2=[]
# sc = ax.scatter(x,y)
# sc2 = ax.scatter(x,y2)
# plt.xlim(0,4000)
# plt.ylim(-6e-12,2e-11)
# plt.legend(['Average','Standard Deviation'])
# plt.draw()

# avg = []
# std = []
# times = []
# #code repeats for an hour
# time_start = datetime.datetime.now()
# while (datetime.datetime.now() - time_start).total_seconds() < 3600:
#     output = p.multi_readings()
#     a = float(output.split(',')[0])
#     s = float(output.split(',')[1])
#     t = int((datetime.datetime.now() - time_start).total_seconds())
#     avg.append(a)
#     std.append(s)
#     times.append(t)
#     x.append(t)
#     y.append(a)
#     y2.append(s)
#     sc.set_offsets(np.c_[x,y])
#     sc2.set_offsets(np.c_[x,y2])
#     fig.canvas.draw_idle()
#     plt.pause(0.1)
# plt.ylim(min(y+y2),max(y+y2))
# print('done')
# #plt.waitforbuttonpress()


# rows = zip(times,avg,std)
# with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\noise_hunt\\'+filename+'.csv', 'w',newline='') as f:
#     writer = csv.writer(f)
#     for row in rows:
#         writer.writerow(row)  


# #%% Just reading normal data

# def setup():
#     ser = serial.Serial(
#         port='COM9',
#         baudrate=9600,
#         bytesize=serial.EIGHTBITS,
#         parity=serial.PARITY_NONE,
#         stopbits=serial.STOPBITS_ONE,
#         timeout=None)
#     ser.write(('SYST:ZCH ON' + '\r\n').encode()) 
#     print("\n\nDettach current source from picoammeter...")
#     input("Press [ENTER] to continue......")    
#     ser.write(('*RST' + '\r\n').encode())
#     ser.write(('SENS:CURR:RANG 2e-9' + '\r\n').encode())
#     ser.write(('SENS:CURR:NPLC 10' + '\r\n').encode()) #60
#     ser.write(('INIT' + '\r\n').encode())
#     ser.write(('SYST:ZCOR:ACQ' + '\r\n').encode())
#     ser.write(('SYST:ZCOR ON' + '\r\n').encode()) 
#     print("\n\nAttach current source to picoammeter...")
#     input("Press [ENTER] to continue......")    
#     ser.write(('SYST:ZCH OFF' + '\r\n').encode())
#     ser.write(('SYST:AZER ON' + '\r\n').encode())
#     return(ser)

# def read(ser):
#     ser.write(('FORM:ELEM READ' + '\r\n').encode())
#     ser.write(('ARM:SOUR IMM' + '\r\n').encode())
#     ser.write(('TRIG:COUN 20' + '\r\n').encode())
#     ser.write(('TRAC:POIN 20' + '\r\n').encode())
#     ser.write(('TRAC:FEED SENS' + '\r\n').encode())
#     ser.write(('TRAC:FEED:CONT NEXT' + '\r\n').encode())
#     ser.write(('INIT' + '\r\n').encode())
#     ser.write(('TRAC:DATA?' + '\r\n').encode())
#     out = ''
#     response = ser.readline()
#     out = response.decode('utf-8')
#     out = (out.strip('\n')).split(',')
#     out = [float(i) for i in out]
#     return out
#%%


#%%%
# p = Pico()
# p.open_connection()
# p.setup()

# reads=[]
# for i in range(50):
#     data=p.raw_readings()
#     reads.extend(data.split(','))
#     reads.remove('')

# rows = zip(reads)
# with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\noise_hunt\\raw.csv', 'w',newline='') as f:
#     writer = csv.writer(f)
#     for row in rows:
#         writer.writerow(row)  
#%%
plt.ion()
f = plt.figure()
f.set_figheight(7)
f.set_figwidth(10)
graph1 = f.add_subplot(221)
graph2 = f.add_subplot(222)
graph3 = f.add_subplot(223)
graph4 = f.add_subplot(224)

x, y = [],[]
y2=[]
def graph(x,y,y2,reads):
    graph1.clear()
    graph2.clear()
    graph3.clear()
    graph4.clear()
    graph1.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
    graph1.set_title('Median w/ Std Error')
    graph2.errorbar(x,y,yerr=y2,fmt='o',capsize=3)
    graph2.set_title('Median w/ Std Error (log)')
    graph2.set_yscale('log')
    graph3.plot(reads)
    graph3.set_title('Raw data')
    graph4.plot(reads)
    graph4.set_title('Raw data (log)')
    graph4.set_yscale('log')
    f.canvas.draw()
    f.canvas.flush_events()
reads=[]
graph(x,y,y2,reads)
ser = Pico.setup()

# dark=[]
# for i in range(5):
#     data=Pico.read(ser)
#     dark.extend(data)
#     print(np.median(dark))
# d_med=np.median(dark)
# d_std=np.std(dark)



for i in range(1):
    try:
        data,response=Pico.read(ser)
        reads.append(data)
        x.append(i)
        y.append(np.median(data))
        y2.append(np.std(data)/np.sqrt(len(data)))
        print("Median = {:.2e} Std.Error = {:.2e}".format(y[-1],y2[-1]))
        graph(x,y,y2,reads)
        i+=1
    except(KeyboardInterrupt):
        Pico.close_connection(ser)
Pico.close_connection(ser)
rows = zip(x,reads)
with open('C:\\Users\\sesel\\OneDrive - Arizona State University\\LASI-Alpha\\Documents\\pico_data\\noise_hunt\\051524_allnight.csv', 'w',newline='') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)  

#Pico.close_connection(ser)


#%%
'''
Below are all the function calls that you would use to setup the picoammeter and then close it
'''
# p = Pico()
# p.open_connection()
# p.setup()
# p.close_connection()