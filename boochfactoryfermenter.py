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
#import sys package for error handling sys.exit()
import sys

#everythign in the try block will attempt to be executed
#on failure OR completion, the finally: block will be executed
try:

    #set GPIO mode and pins
    GPIO.setmode(GPIO.BOARD)
    #Set "status" LED pin number
    statusLEDpin = 7
    GPIO.setup(statusLEDpin, GPIO.OUT)
    #set "heating" LED pin nmber
    heatingLEDpin = 13
    GPIO.setup(heatingLEDpin, GPIO.OUT)
    
    #set minimum and max booch temp in deg F
    #heater turns on a min temp and off at max temp
    minTemp = 86
    maxTemp = 88
    
    #set heater realy pin number
    heaterRelayPin = 15

    #setup the output log file
    #Open boochlog.txt in the home directory inappend mode. If it does not exist, create it.
    log = open("/home/pi/boochlog.txt", "a+")


    ##############################################
    #Thermometer setup stuff
    #set ds1820 thermometer prefix
    ds1820_prefix = '28'
    #thermometer calibration - if a thermo reads consistenaly high or low, adjust it here by offseting the reading in degrees F. Does accept negative numbers
    thermAdjust = 0
    #base directory for thermometer readings
    devices_base_dir ='/sys/bus/w1/devices/'
    #find the output file for the thermometer
    therm_folder = glob.glob(devices_base_dir + ds1820_prefix + '*')[0]
    therm_file = therm_folder + '/w1_slave'
    #initiate
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
              


    #functions to read the temp of the thermometer
    def read_temp_raw():
        with open(therm_file, 'r')as deviceFile:
            lines=deviceFile.readlines()
        return lines

    def degCtoF(tempC):
        return 9.0/5.0 * tempC + 32

    def read_temp():
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            return float(temp_string) / 1000.0

    #functions to set LED states
    def statusLEDon():
        GPIO.output(statusLEDpin,True)
        
    def statusLEDoff():
        GPIO.output(statusLEDpin,False)
        
    def heatingLEDon():
        GPIO.output(heatingLEDpin,True)
        
    def heatingLEDoff():
        GPIO.output(heatingLEDpin,False)
        
    #functions to control the heater state via the relay and handle errors in temp sensing    
    def setHeaterState(state):
        if state == "ON":
            #whatever pinstate turns the relay on :::: GPIO.output(heaterRelayPin, True)
            heatingLEDon()
        elif state == "OFF":
            #whatever pinstate turns the relay OFF :::: GPIO.output(heaterRelayPin, False)
            heatingLEDoff()
        else:
            print("Invalid heater state. Aborting.")
            GPIO.cleanup()
            
    def crazyCheckTemp(tempReading):
        if tempReading <= 35 and tempReading >= 29:
            log.write('Thermometer disconnected! Abort!')
            GPIO.cleanup()
            sys.exit()
        if tempReading <= 60:
            log.write('Temp abnormally low! Abort!')
            GPIO.cleanup()
            sys.exit()
        if tempReading >= 85:
            log.write('Temp abnormally high! Abort!')
            GPIO.cleanup()
            sys.exit()
        else:
            return "CrazyPass"
    

            

    #############
    # MAIN LOOP #
    #############
    for i in range(10):
        statusLEDon()
        
        #create timestamp
        today=datetime.datetime.now()
        timestamp = str(today.strftime('%Y, %m, %d, %H, %M, %S'))
        
        #get host
        host = str(socket.gethostname())
        
        #get temp
        currentTemp = degCtoF(read_temp()) + thermAdjust
        #error check the temp - abort if crazy reading
        crazyCheckResult = crazyCheckTemp(currentTemp)
        

        
        if currentTemp <= minTemp:
            heaterState = "ON"
        elif currentTemp >= maxTemp:
            heaterState = "OFF"
                  
        setHeaterState(heaterState)
    
        #assemble the message to log
        message = host + ', ' + timestamp + ', ' + str(currentTemp) + ' ' + crazyCheckResult + '\n'
        
        print(message)
        log.write(message)
        
        statusLEDoff()
        time.sleep(.3)        


except KeyboardInterrupt:
    print('Program haulted by keyboard input. Aborting!')
    GPIO.cleanup()
    sys.exit()
    
except:
    print('Unexpected error. Aborting.')
    GPIO.cleanup()
    sys.exit()


#finally is always executed even if there is an error in the try block
#put all the cleanup stuff here. This will always run, so don't have it do the emergency abort / turn off heater.
finally:
    #close the log file
    log.close()
    #clean up the GPIO pin settings EXCEPT the heating pad LED and relay
    GPIO.cleanup(statusLEDpin)
    #show completion in terminal
    print('End')








