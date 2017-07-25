#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import tools
import config
import traceback
import os
from urllib2 import URLError
from logger import *  

read_log_file = open(config.read_log, "w")
send_log_file = open(config.send_log, "w")

global machine_status
global machine_last_status
machine_status = config.machine_status_other
machine_last_status = config.machine_status_other

lock = threading.Lock()

coffee_paid = False
machine_is_ready = False
global read_serial_name
read_serial_name = ""

#write cmd logs into files
def printCmdLog(line, direction):
	if(direction == "send" and config.logFile == "True"):
		send_log_file.write(line + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		send_log_file.flush()
	elif(direction == "read" and config.logFile == "True"):
		read_log_file.write(line + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		read_log_file.flush()

def processReadCmd(line):
	global machine_status
	global machine_last_status
	global machine_is_ready
	if(tools.isCmd(line, config.heartbeat2)):
		lock.acquire()
		machine_is_ready = True
		machine_status = config.machine_status_ok
		lock.release()
	
	is_error = False
	#if(machine_status == config.machine_status_ok or machine_status == config.machine_status_busy):
	if(machine_status == config.machine_status_ok):
		if(tools.isCmd(line, config.EmptyDripTray)):
			info( "got EmptyDripTray")
			is_error = True
		elif(tools.isCmd(line, config.OutOfWaterBox)):
			info( "got OutOfWaterBox")
			is_error = True
		elif(tools.isCmd(line, config.OutOfWater)):
			info( "got OutOfWater")
			is_error = True
		elif(tools.isCmd(line, config.OutOfBean)):
			info( "got OutOfBean")
			is_error = True
		elif(tools.isCmd(line, config.FullOfWasteWater)):
			info( "got FullOfWasteWater")
			is_error = True
		elif(tools.isCmd(line, config.FullOfDrogs)):
			info( "got FullOfDrogs")
			is_error = True
		elif(line.startswith(config.coffeeConfirm)):
			info( "got coffee confirm from mainboard.")

	#paid and out of beans ,so refund and set status to server
	if(machine_status == config.machine_status_busy and tools.isCmd(line, config.OutOfBean)):
		is_error = True
		info( "got OutOfBean begin to refund()")
		tools.refund()
	#if current status is alert ,so ommit this error, because error status already set before.
	if(is_error == True and machine_status != config.machine_status_alert):
		lock.acquire()
		info( "machine's current status is:" + str(machine_status))
		machine_last_status = machine_status
		machine_status = config.machine_status_alert
		info( "set alert status of machine: to the server" + str(machine_status))
		lock.release()

def payService():
    #when program start running, set machine's status is error to prevent user do pay action.
    #tools.post_machine_error()
    global machine_status
    global machine_last_status
    global lock
    global machine_is_ready
    while True:
	if(machine_is_ready == False):
		time.sleep(1)
		continue

	global coffee_paid
	status = tools.get_status()
	getresult = int(status)

        if(getresult == 1 and coffee_paid == False):
		lock.acquire()
                info( "got coffe payed! begin to produce!")
		coffee_paid = True
		#tools.post_machine_busy()
		#machine_last_status = machine_status
		machine_last_status = machine_status#this will blind set machine status to busy
		machine_status = config.machine_status_busy
		machine_is_ready = False
		lock.release()
		info("set machine_is_ready is false")
	elif getresult == 20:
		info( "got reboot message!")
		#write status into files
		tools.do_reboot()
        else:
                info( "no coffe or error or busy! status is : " + status) 
	time.sleep( 4 )
	#try:  
	#	tools.checkNewVersion(config.update_url)
	#except KeyboardInterrupt:  
	#	info( "get KeyboardInterrupt")
	#	tools.reload()
	
def waitMachineReady(deviceName):
	i=0
	global machine_status
	global machine_is_ready
	global read_serial_name
	serialLine = serial.Serial(deviceName, config.BaudRate, stopbits=config.stopbits_int, timeout=10, write_timeout=10)
	while True:  
		if(i == 10):
			info( "got 10 heartbeat2 and set machine_is_ready=True and machine_status=ok, deviceName is : " + deviceName)
			machine_status = config.machine_status_ok
			machine_is_ready = True
			read_serial_name = serialLine #need to switch serial line
			info("set machine_is_ready is true")
			break

		elif(machine_is_ready):
			info( "other thread set machine_is_ready=True")
			break

		time.sleep(0.1)  
		line = serialLine.readline()
		info( line)
		if(tools.isCmd(line, config.heartbeat2)):
			info( "got line is heartbeat2")
			i = i + 1
		serialLine.write(line) 
		serialLine.flushInput()

	if serialLine != None:  
		serialLine.close()  
		time.sleep(0.1)


#basic logic for serial
def serialThread(deviceName, isSendLine):  
	global coffee_paid
	info( "deviceName is " + deviceName)
	serialLine = serial.Serial(deviceName, config.BaudRate, stopbits=config.stopbits_int, timeout=10, write_timeout=10)
	#open HMI-->mainboard serial line, to communicate.
	while True:  
		try:
			time.sleep(0.1)  
			line = serialLine.readline()


			if(isSendLine):
				printCmdLog(line,"send")
				if(tools.filterSendCmd(line)):
					continue
			
			else:
				printCmdLog(line,"read")
				processReadCmd(line)
			

			if(isSendLine and coffee_paid):
				try:
					serialLine.write(config.longcoffee)
					#serialLine.write(config.espresso)
					#serialLine.write(config.hotwater)
					coffee_paid = False
				except 	SerialTimeoutException:
					info( "got SerialTimeoutException because of write send serial")
					tools.reload()
			else:
				serialLine.write(line) 

			serialLine.flushInput()
			#shutdown button pressed or auto shutdown ,reboot raspberri
			if(line == config.shutdown or line == config.sys_error):
				tools.do_reboot()

		except :
			print 'traceback.print_exc():'; traceback.print_exc()
			info( "got SerialException because of write read serial")
			tools.reload()


def main():  
	global coffee_paid
	#get usb devices name
	usbDevices = tools.getUSBDevices()

	ser_read_str = usbDevices[1]
	ser_send_str = usbDevices[0]
	info( "ser_read_str is " + ser_read_str)
	info( "ser_send_str is " + ser_send_str)
	while True:  
		if(tools.isPowerOff(ser_read_str, ser_send_str) == True):
			info( "machine is power off")
			time.sleep(2)  
		else:
			break

	#check new version
	#tools.checkNewVersion(config.update_url)

############################################################new modify
	
	#start threads to test machine is ok
	thread.start_new_thread( waitMachineReady, (ser_read_str,) )
	thread.start_new_thread( waitMachineReady, (ser_send_str,) )
	#wait machine is ok
	while(machine_is_ready == False):
		info("machine still polling")
		time.sleep(0.1)
	if(read_serial_name != ""):#need switch serial
		ser_read_str = usbDevices[0]
		ser_send_str = usbDevices[1]

	thread.start_new_thread( serialThread, (ser_read_str,False,) )
	thread.start_new_thread( serialThread, (ser_send_str,True,) )



	#start thread to connect with server to get pay info.
	thread.start_new_thread( payService, () )



	#when machine's status changed ,synchronized status to the server.
	#thread.start_new_thread( syncMachineStatus, () )
	global machine_status
	global machine_last_status
	global lock
	while True:
		time.sleep(0.2)
		if(machine_status != machine_last_status):
			info( "in syncMachineStatus will send status to the server : " + str(machine_status))
			#tools.sendPostMessage(config.url, config.acid, config.operation_set, machine_status)
			machine_last_status = machine_status
			time.sleep(1)


if __name__ == '__main__':  
    try:  
	info("begin to start")
	main()
    except KeyboardInterrupt:  
	info( "get KeyboardInterrupt")
	tools.reload()

    except serial.serialutil.SerialException:
	info( "got serial.serialutil.SerialException so reload")
	tools.reload()
    except urllib2.HTTPError, e:
	info( "got urllib2.HTTPError so reload")
	tools.reload()
    except urllib2.URLError, e:
	info( "got urllib2.URLError so reload")
	tools.reload()
    except Exception, e:
	info( "got exception so reload")
        print 'str(Exception):\t', str(Exception)
	print "got exception so reload "
        print 'traceback.print_exc():'; traceback.print_exc()
	time.sleep(2)
	print "after to sleep 2"
	tools.reload()

