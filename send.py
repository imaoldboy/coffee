#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import tools
import config

havecoffee = 1
getresult = 0

send_log_file = open(config.send_log, "w")


ser_send= serial.Serial(config.serial_send_fd, config.BaudRate, stopbits=config.stopbits_int)

machine_is_error = True

def coffeeService(url):
    while True:
	global getresult
	print "in coffeeService ,begin to get status"
	returnData = tools.get_status()
        getresult = int(returnData)
	print "getresult is : %d" % getresult

        if havecoffee == getresult:
                print "got coffe payed! begin to produce!"
                tools.produce_coffee(ser_send)
		
		try:
			config.lock.acquire()
		except:
			print "exception in lock.acqurie"
		finally:
			config.lock.release()

		time.sleep(0.2)
		tools.post_machine_busy()
		getresult = 0
		#must improve use lock way
                time.sleep( 40 )
		tools.post_machine_ok()
		config.lock.release()
        else:
                print "no coffe or error!"
                time.sleep( 4 )
def main():  

	#check new version
	newVersion = tools.update(config.update_url)
	if(newVersion != "na"):
		tools.get_new_version(newVersion)
		tools.do_update()
		raise KeyboardInterrupt 
	#start thread to connect with server.
	thread.start_new_thread( coffeeService, (config.url,) )

	#open HMI-->mainboard serial line, to communicate.
	while True:  
		line = ser_send.readline()
		needFilter = tools.filterCmd(send_log_file, "", line,"send")
		if(needFilter):
			continue
		ser_send.write(line) 
		ser_send.flushInput()
		time.sleep(0.1)  


if __name__ == '__main__':  
    try:  
	main()
    except KeyboardInterrupt:  
	print "get KeyboardInterrupt"
	if ser_send != None:  
            ser_send.close()  

