#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import config
import os
import commands
import traceback
from logger import *  

def refund():
	returnData = sendPostMessage(config.refund_url, config.acid, "", "")
	info("after refund() result is: " + returnData)
	
def getUSBDevices():
	return commands.getoutput('ls /dev/ttyUSB*').split("\n")

def isPowerOff(device1,device2):
	ser_test1 = serial.Serial(device1, config.BaudRate, stopbits=config.stopbits_int, timeout=5)
	ser_test2 = serial.Serial(device2, config.BaudRate, stopbits=config.stopbits_int, timeout=5)
	try:
		line1 = ser_test1.readline()
		ser_test1.write(line1) 
		ser_test1.flushInput()
		time.sleep(0.1)

		line2 = ser_test2.readline()
		ser_test2.write(line2) 
		ser_test2.flushInput()
		time.sleep(0.1)
		if(len(line1)>3 or len(line2)>3):
			info( "got ttyUSB0 or ttyUSB1 as alive" )
			return False
		else:
			return True
	except	serial.SerialException:
		info( "isPowerOff() ttyUSB0 ")
		return True
	finally:
		if ser_test1 != None:  
			ser_test1.close()  
		if ser_test2 != None:  
			ser_test2.close()  

def isCmd(line, cmdStr):
	if(cmp(cmdStr[7:9], line[7:9])==0 and cmp(cmdStr[15:17], line[15:17])==0):
		return True
	else:
		return False

def reload():
	info( "begin reload")
	post_machine_error()
	os.system('/bin/sh /home/pi/python/reload.sh')

#filter cmd in order to prevent user touch.
def filterSendCmd(line):
	if(config.filterCmd == "True"):
		for i in range(len(config.filter_send_cmd_array)) :  
			if(config.filter_send_cmd_array[i] == line):
				return True

#write cmd logs into files
def printCmdLog(send_log_file, read_log_file, line, direction):
	if(direction == "send" and config.logFile == "True"):
		send_log_file.write(line + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		send_log_file.flush()
	elif(direction == "read" and config.logFile == "True"):
		read_log_file.write(line)
		read_log_file.flush()

# not used now
def produce_coffee(ser_send):
	info( "begin to produce coffee!")	
	ser_send.write(config.espresso)
	#ser_send.write(config.hotwater)
	ser_send.flushInput()
	ser_send.write(config.hotwater_confirm)
	ser_send.flushInput()
	#lock.acquire()

def post_out_of_beans():
	info( "machine is out of beans")
	returnData = sendPostMessage(config.url, config.acid, config.operation_set, config.machine_status_bean_water)
def post_out_of_water():
	info( "machine is out of water")
	returnData = sendPostMessage(config.url, config.acid, config.operation_set, config.machine_status_bean_water)

def post_machine_error():
	info( "machine is out of service")
	returnData = sendPostMessage(config.url, config.acid, config.operation_set, config.machine_status_alert)

def post_machine_busy():
	info( "machine is busy")
	returnData = sendPostMessage(config.url, config.acid, config.operation_set, config.machine_status_busy)

def post_machine_ok():
	info( "machine is ok")
	returnData = sendPostMessage(config.url, config.acid, config.operation_set, config.machine_status_ok)

def checkNewVersion(url):
	returnData = sendPostMessage(url, config.acid, config.operation_check, "")
        if returnData != "na":
		#wget send.py
                info( "got new version! url is : " + returnData)
		do_download(returnData)
		update_done(url)
		raise KeyboardInterrupt 


def update_done(url):
	info( "in update_done()")
	returnData = sendPostMessage(url, config.acid, config.operation_done, "")

def do_download(fileUrl):
	info( "begin to download new version file!")
	os.chdir('/home/pi/python')
	os.system('rm -f all.py')
	os.system('rm -f config.py')
	os.system('rm -f tools.py')
	os.system('wget www.usertech.cn/app/uploads/2016/all.py')
	os.system('wget www.usertech.cn/app/uploads/2016/config.py')
	os.system('wget www.usertech.cn/app/uploads/2016/tools.py')
	#os.system('wget -r -P /home/pi/python/ ' +fileUrl)
	#os.system('wget ' +fileUrl)
	#info( "begin to reload in do_update()")
	#reload()

def do_reboot():
	info( "begin to do_reboot")
	os.chdir('/home/pi/python')
	open('/home/pi/python/coffee.log','w').close()
	os.system('sudo chown pi:pi /home/pi/python/coffee.log')
	#os.system('echo > coffee.log')
	os.system('sudo reboot')

def checkReboot():
	#info( "in checkReboot()")
	if(get_status() == "20"):
		info( "begin to reboot")
		do_reboot()

def get_status():
	return sendPostMessage(config.url, config.acid, config.operation_get, "")

def sendPostMessage(url,acid, op, va):
	#info( "=================below is op")
	#info( op)
	#info( va)
	#info( "above is va =================")
	result = ""
	while True:
		try:
			data = urllib.urlencode({'acid':acid, 'op':op, 'va': va})
			req = urllib2.Request(url, data)
			response = urllib2.urlopen(req, timeout=5)
			result = response.read()
			break
		except Exception, e:
			info( "get exception in sendPostMessage() begin to sleep 2 seconds ")
			print 'traceback.print_exc():'; traceback.print_exc()
			time.sleep(2)
	return result


