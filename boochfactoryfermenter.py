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
    minTemp = 79
    maxTemp = 80
    
    #set heater realy pin number
    heaterRelayPin = 15
    #I would prefer a realy that was default off on configuring as OUTPUT, but that is a future upgrade.....
    GPIO.setup(heaterRelayPin, GPIO.OUT)
    
    #setup the output log file
    #Open boochlog.txt in the home directory inappend mode. If it does not exist, create it.
    log = open("/home/pi/boochlog.txt", "a+")
    
    #setup the heater state perisistant value file
    #using a file instead of pickle or shelve because easier to read outside of program
    heaterStatePersist = open("/home/pi/heaterStatePersist.txt", "a")
    heaterStatePersist.close()

    with open("/home/pi/heaterStatePersist.txt", "r") as heaterStatePersist:
        previousHeaterState = heaterStatePersist.read()


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
        
    #functions to control the heater state and persist the state for reading by future executions
        #I would prefer a relsy that was default off on configuring as OUTPUT, but that is a future upgrade wih different hardware.....
    def setHeaterState(state):
        if state == "ON":
            GPIO.output(heaterRelayPin, False) #False turns the relay on
            with open("/home/pi/heaterStatePersist.txt", "w") as heaterStatePersist:
                heaterStatePersist.write('ON')
            heatingLEDon()
        elif state == "OFF":
            GPIO.output(heaterRelayPin, True) #False turns the relay off
            with open("/home/pi/heaterStatePersist.txt", "w") as heaterStatePersist:
                heaterStatePersist.write('OFF')
            heatingLEDoff()
        else:
            print("Invalid heater state. Aborting.")
            log.write("Invalid heater state. Aborting.")
            GPIO.cleanup()
    
    #sanity check on temperature readings that will detect prolems with the thermometer
    def crazyCheckTemp(tempReading):
        if tempReading <= 35 and tempReading >= 29:
            return 'Thermometer disconnected! Abort!'
        if tempReading <= 60:
            return 'Temp abnormally low! Abort!'
        if tempReading >= 95:
            return 'Temp abnormally high! Abort!'
        else:
            return "CrazyPass"
    
    #grab the CPU temp for monitoring because we will put the Raspberry Pi in an enclosure and it may overheat
    def getCPUtemperature():
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n",""))
            

    #############
    # MAIN LOOP #
    #############
    for i in range(1):
        statusLEDon()
        
        #create timestamp
        today=datetime.datetime.now()
        timestamp = str(today.strftime('%Y, %m, %d, %H, %M, %S'))
        
        #get host
        host = str(socket.gethostname())
        
        #get CPU temp
        cpuTemp = getCPUtemperature()
                                               
        #get temp
        currentTemp = degCtoF(read_temp()) + thermAdjust
        
        #get current state of heater (to let it coast down to the min temp if below min and max temps
        print(str(previousHeaterState))        
        
        #error check the temp - abort if crazy reading
        crazyCheckResult = crazyCheckTemp(currentTemp)
        
        newHeaterState=str(previousHeaterState)
        if currentTemp <= minTemp:
            newHeaterState = "ON"
        elif currentTemp >= maxTemp:
            newHeaterState = "OFF"
                  
        setHeaterState(newHeaterState)
    
        #assemble the message to log
        message = host + ', ' + timestamp + ', ' + str(currentTemp) + ', ' + crazyCheckResult + ', HeaterStatus: ' + newHeaterState + ', CPU Temp: ' + cpuTemp + '\n'
        
        print(message)
        log.write(message)
        
        if crazyCheckResult != 'CrazyPass':
            GPIO.cleanup()
            sys.exit()
        
        #these line represent a sucessful completion of the main loop
        #after they are executed, the FINALLY will be executed.
        #really the only function is to pause long enough for the status LED to be visible
        time.sleep(.3)  
        statusLEDoff()
      


except KeyboardInterrupt:
    log.write('Program haulted by keyboard input. Aborting!')
    GPIO.cleanup() #this will turn the relay off
    sys.exit()
    
except:
    log.write('Unexpected error. Aborting.')
    GPIO.cleanup() #this will turnthe relay off
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
