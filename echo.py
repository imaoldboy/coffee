#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import tools

url = "http://123.56.18.141/acphp/acstate.php"
acid = "2017051304280377"
havecoffee = 1
getresult = 0

lock = threading.Lock()

serial_read_fd = "/dev/ttyUSB0"
serial_send_fd = "/dev/ttyUSB1"

readFile_log = open("read.txt", "w")
writeFile_log = open("write.txt", "w")

stopbits_int = 2
BaudRate = 38400

ser_read= serial.Serial(serial_read_fd, BaudRate, stopbits=stopbits_int)

try:
	ser_send = serial.Serial(serial_send_fd, BaudRate, stopbits=stopbits_int)
except	serial.SerialException:
        serial_send_fd = "/dev/ttyUSB2"
	ser_send = serial.Serial(serial_send_fd, BaudRate, stopbits=stopbits_int)
        print "reopen ser_send as ttyUSB2"



#message from HMI-->MainBoard
heartbeat        = ":01040000000BF0\r\n"
espresso         = ":010600010001F7\r\n"
hotwater         = ":010600010003F5\r\n"
hotwater_confirm = ":01060001000AEE\r\n"
hotwater2        = ":010600010003F5\r\n:01060001000AEE\r\n"


#message from MainBoard-->HMI
heartbeat2       = ":0104000213000000000000"
EmptyDripTray    = ":0104000313000000000100"
OutOfWaterBox    = ":0104000313000000000200"
OutOfWater       = ":0104000123500000000200"
OutOfBean        = ":0104000310000000000400"
FullOfWasteWater = ":0104000313000000000400"
FullOfDrogs      = ":0104000313000000000500"
CoffeeReady      = ""

machine_is_error = True

def produce_coffee():
	print "begin to produce coffee!"	
	#ser_send.write(espresso)
	ser_send.write(hotwater)
	#lock.acquire()


def processReadCmd(line):
	global machine_is_error
	if(machine_is_error):
		if(line.startswith(heartbeat2)):
			returnData = tools.sendPostMessage(url, acid, "set", 0)
			machine_is_error = False

		else:
			return
	cmdNumber = "0"
	if(line.startswith(EmptyDripTray)):
		cmdNumber = "4"
		machine_is_error = True
	elif(line.startswith(OutOfWaterBox)):
		cmdNumber = "4"
		machine_is_error = True
	elif(line.startswith(OutOfWater)):
		cmdNumber = "3"
		machine_is_error = True
	elif(line.startswith(OutOfBean)):
		cmdNumber = "3"
		machine_is_error = True
	elif(line.startswith(FullOfWasteWater)):
		cmdNumber = "4"
		machine_is_error = True
	elif(line.startswith(FullOfDrogs)):
		cmdNumber = "4"
		machine_is_error = True
	if(machine_is_error):
		returnData = tools.sendPostMessage(url, acid, "set", cmdNumber)

def post_clear_pay_info():
        print "coffee made, clear this machine's pay info"
        returnData = tools.sendPostMessage(url, acid, "set", "0")
        if(returnData == "ok"):
                print "clear pay info success!"
        else:
                print "clear pay info error!"	

def coffeeService(url):
    while True:
	global getresult
	returnData = tools.sendPostMessage(url, acid, "get", "")
        getresult = int(returnData)
#	print "getresult is : %d" % getresult

        if havecoffee == getresult:
                print "got coffe payed! begin to produce!"
                produce_coffee()

		getresult = 0
		#must improve use lock way
                time.sleep( 45 )
		post_clear_pay_info()
        else:
#                print "no coffe or error!"
                time.sleep( 4 )
def main():  
	thread.start_new_thread( coffeeService, (url,) )
	while True:  
		line = ser_send.readline()
		tools.filterCmd(writeFile_log, readFile_log, line,"send")

		ser_send.write(line) 
		ser_send.flushInput()
		time.sleep(0.1)  

		line = ser_read.readline()

		tools.filterCmd(writeFile_log, readFile_log, line,"read")
		#
		processReadCmd(line)

		ser_read.write(line)
		ser_read.flushInput()
		time.sleep(0.1)


if __name__ == '__main__':  
    try:  
	main()
    except KeyboardInterrupt:  
        if ser_send != None:  
            ser_send.close()  
	if ser_read != None:  
            ser_read.close()  

