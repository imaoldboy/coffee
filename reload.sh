#nohup python -u send.py > send.log 2>&1 &
#nohup python -u receive.py > receive.log 2>&1 &
sudo killall python
nohup python -u /home/pi/python/all.py > /home/pi/python/all.log 2>&1 &
