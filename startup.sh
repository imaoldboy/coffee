#nohup python -u send.py > send.log 2>&1 &
#nohup python -u receive.py > receive.log 2>&1 &
>/home/pi/python/coffee.log
>/home/pi/python/all.log
/bin/chown pi:pi /home/pi/coffee/coffee.log
/bin/chown pi:pi /home/pi/coffee/all.log
nohup python -u /home/pi/coffee/all.py > /home/pi/coffee/all.log 2>&1 &
#nohup python -u all.py > all.log 2>&1 &
