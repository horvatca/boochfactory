#import socket to be abel to find the hostname of the rpi
import socket
#import GPIO package
import RPi.GPIO as GPIO
#import time package
import time
#import date and time package for inserting date into logs
import datetime
#import glob package used for finding files and paths according to patterns and Unix rules
import glob
#import os package for executing shell commands amd other useful OS stuff.
import os


#set GPIO mode and pins
GPIO.setmode(GPIO.BOARD)
#Set LED pin number
GPIO.setup(7, GPIO.OUT)

##############################################
#Thermometer setup stuff
#set ds1820 thermometer prefix
ds1820_prefix = '28'
#base directory for thermometer readings
devices_base_dir ='/sys/bus/w1/devices/'
#find the output file for the thermometer
therm_folder = glob.glob(devices_base_dir + ds1820_prefix + '*')[0]
therm_file = therm_folder + '/w1_slave'
#initiate
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
          


#functions to read the temp fo the thermometer
def read_temp_raw():
    with open(therm_file, 'r')as deviceFile:
        lines=deviceFile.readlines()
    return lines

def degCtoF(tempC):
    return tempC * 9.0 / 5.0 + 32

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        return float(temp_string) /1000.0



#############
# MAIN LOOP #
for i in range(2):
    GPIO.output(7,True)
    time.sleep(1)
    #test printing the date and time
    today=datetime.datetime.now()
    print(socket.gethostname() + ' ' + today.strftime('%Y, %m, %d, %H, %M, %S') + ', ' + str(read_temp()))
    GPIO.output(7,False)
    time.sleep(1)

print('end')
GPIO.cleanup()









