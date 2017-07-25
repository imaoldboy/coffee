#!/usr/bin/env python
import threading
import thread
import urllib2
import urllib
import serial  
import time  
import config


global url
global acid

global serial_read_fd
global serial_send_fd

global read_log
global send_log

global stopbits_int
global BaudRate
global logFile
global all_log_file


#message from HMI-->MainBoard
global sys_error
global shutdown
global clean
global longcoffee
global cappuccino
global coffeelatte
global milkcream
global turnleft
global turnright
global heartbeat
global espresso
global hotwater
global hotwater_confirm
global hotwater2


#message from MainBoard-->HMI
global heartbeat2
global EmptyDripTray
global OutOfWaterBox
global OutOfWater
global OutOfBean
global FullOfWasteWater
global FullOfDrogs
global CoffeeReady

global machine_status_ok
global machine_status_paid
global machine_status_busy
global machine_status_bean_water
global machine_status_alert
global machine_status_other
global machine_status_ok_timeout
global machine_status_paid_timeout
global machine_status_busy_timeout
global machine_status_bean_water_timeout
global machine_status_alert_timeout
global machine_status_other_timeout
global machine_status_need_restart

global operation_set
global operation_get

global filter_send_cmd_array
global filterCmd

#global lock
#lock = threading.Lock()
logFile = "False"
all_log_file = "/home/pi/python/coffee.log"
#url       ="http://123.56.18.141/acphp/acstate.php"
url       ="http://101.200.80.132:3000/"
#url       ="http://www.usertech.cn:3000/"
update_url="http://123.56.18.141/acphp/acupdates.php"
refund_url="http://123.56.18.141/acphp/acrefund.php"
acid      = "2017040608444680"

serial_read_fd = "/dev/ttyUSB1"
serial_send_fd = "/dev/ttyUSB0"

read_log = "read.log"
send_log = "send.log"

stopbits_int = 2
BaudRate = 38400


#message from HMI-->MainBoard
filter_send_cmd_array = (":010600010508EB\r\n",":010600010005F3\r\n",":010600010006F2\r\n",":010600010007F1\r\n",":010600010509EA\r\n",":010600010409EB\r\n")
filterCmd = "True"

sys_error        = "00000BF0\r\n"
shutdown         = ":010600010004F4\r\n"
clean            = ":010600010508EB\r\n"
longcoffee       = ":010600010002F6\r\n"
cappuccino       = ":010600010005F3\r\n"
coffeelatte      = ":010600010006F2\r\n"
milkcream        = ":010600010007F1\r\n"
turnleft         = ":010600010509EA\r\n"
turnright        = ":010600010409EB\r\n"

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
FullOfDrogs      = ":0104040310000000001100" #FullOfDrogs      = ":0104000313000000000500"
coffeeConfirm    = ":0104052021110000000000"
CoffeeReady      = ""

machine_status_ok = 0
machine_status_paid = 1
machine_status_busy = 2
machine_status_bean_water = 3
machine_status_alert = 4
machine_status_other = 5
machine_status_ok_timeout = 6
machine_status_paid_timeout = 7
machine_status_busy_timeout = 8
machine_status_bean_water_timeout = 9
machine_status_alert_timeout = 10
machine_status_other_timeout = 11
machine_status_need_restart  = 20

operation_set   = "set"
operation_get   = "get"
operation_check = "check"
operation_done  = "done"


