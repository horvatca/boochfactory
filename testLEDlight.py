import socket
print (socket.gethostname())

#import GPIO package
import RPi.GPIO as GPIO
#import timr package
import time

#set GPIO mode and pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

#loop to test LED blink
for i in range(3):
    GPIO.output(7,True)
    time.sleep(1)
    GPIO.output(7,False)
    time.sleep(1)
GPIO.cleanup()
