#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import tools
import config

read_log_file = open(config.read_log, "w")

ser_read= serial.Serial(config.serial_read_fd, config.BaudRate, stopbits=config.stopbits_int)

try:
	ser_send = serial.Serial(config.serial_send_fd, config.BaudRate, stopbits=config.stopbits_int)
except	serial.SerialException:
        serial_send_fd = "/dev/ttyUSB2"
	ser_send = serial.Serial(config.serial_send_fd, config.BaudRate, stopbits=config.stopbits_int)
        print "reopen ser_send as ttyUSB2"

machine_is_error = True

def processReadCmd(line):
	global machine_is_error
	if(machine_is_error):
		status = tools.get_status()
		if(tools.isCmd(line, config.heartbeat2)):
			if(status!="2"):#busy ,is making coffee
				tools.post_machine_ok()
			machine_is_error = False

		else:
			return
	cmdNumber = "0"
	if(tools.isCmd(line, config.EmptyDripTray)):
		cmdNumber = "4"
		machine_is_error = True
		tools.post_machine_error()
	elif(tools.isCmd(line, config.OutOfWaterBox)):
		cmdNumber = "4"
		machine_is_error = True
		tools.post_out_of_beans()
	elif(tools.isCmd(line, config.OutOfWater)):
		cmdNumber = "3"
		machine_is_error = True
		tools.post_out_of_water()
	elif(tools.isCmd(line, config.OutOfBean)):
		cmdNumber = "3"
		machine_is_error = True
		tools.post_out_of_beans()
	elif(tools.isCmd(line, config.FullOfWasteWater)):
		cmdNumber = "4"
		machine_is_error = True
		tools.post_machine_error()
	elif(tools.isCmd(line, config.FullOfDrogs)):
		cmdNumber = "4"
		machine_is_error = True
		tools.post_machine_error()
	elif(line.startswith(config.coffeeConfirm)):
		config.lock.release()
	#if(machine_is_error):
	#	returnData = tools.sendPostMessage(url, acid, "set", cmdNumber)

def main():  
	while True:  
		line = ser_read.readline()

		tools.filterCmd("", read_log_file, line,"read")
		#
		processReadCmd(line)

		ser_read.write(line)
		ser_read.flushInput()
		time.sleep(0.1)


if __name__ == '__main__':  
    try:  
	main()
    except KeyboardInterrupt:  
	if ser_read != None:  
            ser_read.close()  

