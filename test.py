#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import tools
from binascii import unhexlify


port =  "/dev/ttyUSB0"
ser = serial.Serial(port,9600, stopbits=1, timeout=3)
print(ser.name + ' is open.')
  
while True:
    input = raw_input("Enter HEX cmd or 'exit'>> ")
    if input == 'exit':
        ser.close()
        print(port+' is closed.')
        exit()
 
    elif len(input) == 8:
    # user enters new register value, convert it into hex
        newRegisterValue = bits_to_hex(input)
        #ser.write(newRegisterValue.decode('hex')+'\r\n')
        ser.write(newRegisterValue.decode('hex'))
        print('Saving...'+newRegisterValue)
        print('Receiving...')
        out = ser.read(1)
        for byte in out:
            print(byte) # present ascii
  
    else:
        cmd = input
        print('Sending...'+cmd)
        #ser.write(cmd.decode('hex')+'\r\n')
        ser.write(cmd.decode('hex'))
        print('Receiving...')
        out = ser.read(1)
        for byte in out:
            print(byte) # present ascii
