#learning relays
#import socket to be abel to find the hostname of the rpi
import socket
#import GPIO package
import RPi.GPIO as GPIO

#import os package for executing shell commands amd other useful OS stuff.
import os
#import sys package for error handling sys.exit()
import sys
import time


#set GPIO mode and pins
GPIO.setmode(GPIO.BOARD)
#Set relay control signal pin number
relayControlPin = 32
GPIO.setup(relayControlPin, GPIO.OUT) #this will close the relay (ON)
print('On set to output ' + str(GPIO.input(relayControlPin)))
time.sleep(4)
GPIO.output(relayControlPin, True) #this will open the relay (OFF)
print('On output set to True ' + str(GPIO.input(relayControlPin)))
time.sleep(4)
GPIO.output(relayControlPin, False) #this will close the relay (ON)
print('On output set to false ' + str(GPIO.input(relayControlPin)))
time.sleep(4)
GPIO.cleanup() #this will lcose the relay
print('On cleanup ' + str(GPIO.input(relayControlPin)))
#GPIO.cleanup() sets all the chanels back to INPUT, and thus the relay will by defualt go to giving no signal.

    

