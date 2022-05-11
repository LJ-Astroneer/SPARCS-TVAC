# -*- coding: utf-8 -*-
"""
Created on Mon May  2 12:41:31 2022

@author: Logan Jensen
"""

#!/usr/bin/env python3
import pymodbus
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer

port = 'COM5'
baudrate = 115200
client = ModbusClient(
  method = 'rtu'
  ,port='COM5'
  ,baudrate=baudrate
  ,parity = 'O'
  ,timeout=1
  )
client.connect()
registers  = client.read_coils(1,1,unit=1)# start_address, count, slave_id
print (registers)
