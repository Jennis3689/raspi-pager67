import RPi.GPIO as GPIO
import time
from enum import Enum
from datetime import datetime
import csv
import time
import os


r_pin = 11
b_pin = 12
g_pin = 13
button_pin = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(r_pin, GPIO.OUT)
turnedontime = None
turnedofftime = None
elapsedtime = None
fturnedofftime = None
fturnedontime = None


pageronoff = False
CSV_FILE_NAME = "pager_log"
HEADER = ["Turned On", "Turned Off", "Elapsed Time"]
 
def logtocsv(data):
    file_exists = os.path.exists(CSV_FILE_NAME)
    
    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
        csv_writer= csv.writer(csvfile)
        
        if not file_exists:
            csv_writer.writerow(HEADER)
            print(f"Created new CSV file: {CSV_FILE_NAME} with header.")
            
        csv_writer.writerow(data)
        print(f"Logged: {data}")
    
def button_pressed(channel):
    global pageronoff
    global turnedofftime
    global turnedontime
    global elapsedtime
    global fturnedofftime
    global fturnedontime
    
    print("Button Pressed")
    pageronoff = not pageronoff
    match pageronoff:
            case True:
                turnedofftime = datetime.now()
                fturnedofftime = turnedofftime.strftime("%B-%d-%Y %H:%M:%S")
            case False:
                turnedontime = datetime.now()
                fturnedontime = turnedontime.strftime("%B-%d-%Y %H:%M:%S")
                elapsedtime = turnedontime - turnedofftime
                base_datetime = datetime(1, 1, 1)
                felapsedtime = (base_datetime + elapsedtime).strftime("%H:%M:%S")
                
               
                data_to_log = [fturnedontime, fturnedofftime, felapsedtime]
                logtocsv(data_to_log)
                
        
try:
    
    GPIO.add_event_detect(button_pin, GPIO.RISING, callback=button_pressed, bouncetime = 500)
    
    while True:
        match pageronoff:
            case True:
                GPIO.output(r_pin, GPIO.HIGH)
                
            case False:
                GPIO.output(r_pin, GPIO.LOW)
               
                
        
except KeyboardInterrupt:
    GPIO.cleanup()

