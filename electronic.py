#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
from binascii import unhexlify
from logger import *  

serial_fd = "/dev/ttyUSB0"

#electric_log = open("electric.log", "w")

stopbits_int = 1
BaudRate = 9600

ser_line= serial.Serial(serial_fd, BaudRate, stopbits=stopbits_int, timeout=5)

#cmd_str = "B0C0A80101001A"
cmd_str = "\xB0\xC0\xA8\x01\x01\x00\x1A"

def main():  
	while True:  
		print "send:%s" % cmd_str.encode('hex')
		#info(cmd_str.encode('hex'))
		ser_line.write(cmd_str)
		ser_line.flushInput()

		line = ser_line.read(10)
		for character in line:
		  print character.encode('hex')

		time.sleep(1)


if __name__ == '__main__':  
    try:  
	main()
    except KeyboardInterrupt:  
	if ser_line != None:  
            ser_line.close()  

