""" Knight Aerospace Pager Client

This is the client program for the paging network, and is responsible for processing a button press corellated 
another pager inside the network, which will then send a command to page the pager you are pressing for.

Pages are logged inside of the pager_log.csv file, logging the target pager and ip, time turned on, off, and then elapsed time.

When adding new pagers to the network, 


"""


import RPi.GPIO as GPIO
import socket
import time
from enum import Enum
from datetime import datetime
import csv
import os

# Global Variables
CSV_FILE_NAME = "pager_log.csv"
HEADER = ["Target", "Turned On", "Turned Off", "Time Elapsed"]
PORT = 65433
clientHostName = "knight1"

class Pager:
    
    def __init__(self, hostname, ip, buttonPin, LED):
        self.hostname = hostname
        self.ip = ip
        self.LED = LED
        self.buttonPin = buttonPin
        self.paging = False
        self.turnedontime = None
        self.turnedofftime = None
        self.elapsedtime = None
        self.fturnedontime = None
        self.fturnedofftime = None
        self.felapsedtime = None
        
    def togglePage(self):
        global clientHostName
        if self.paging:
            if send_command(f"{clientHostName}:off", self.ip):
                self.paging = False
                self.collectTime(True)
        else:
            if send_command(f"{clientHostName}:on", self.ip):
                self.paging = True
                self.collectTime(False)		
                
    def collectTime(self, turnedOff):
        if turnedOff:
            self.turnedofftime = datetime.now()
            self.fturnedofftime = self.turnedofftime.strftime("%B-%d-%Y %H:%M:%S")
            self.elapsedtime = self.turnedofftime - self.turnedontime
            self.base_datetime = datetime(1, 1, 1)
            self.felapsedtime = (self.base_datetime + self.elapsedtime).strftime("%H:%M:%S")
            data_to_log = [f"{self.hostname} {self.ip}", self.fturnedontime, self.fturnedofftime, self.felapsedtime]
            logtocsv(data_to_log)
        else:
            self.turnedontime = datetime.now()
            self.fturnedontime = self.turnedontime.strftime("%B-%d-%Y %H:%M:%S")
    
    def greenLEDhandler(self):
        GPIO.output(self.LED, self.paging)

class PagerNetworkManager:
    def __init__(self, pager_configs):
        self.pagers = []
        self.buttonPagerMap = {}
        GPIO.setmode(GPIO.BOARD)
        self.load_pagers(pager_configs)
        
    def load_pagers(self, configs):
        for cfg in configs:
            pager = Pager(cfg["hostname"],cfg["ip"], cfg["button_pin"], cfg["led_pin"])
            self.pagers.append(pager)
            self.buttonPagerMap[cfg["button_pin"]] = pager
            GPIO.setup(cfg["button_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(cfg["led_pin"], GPIO.OUT)
            GPIO.add_event_detect(cfg["button_pin"], GPIO.FALLING, callback=self.button_callback, bouncetime=300)
            
    def button_callback(self, pin):
        print(f"Button on pin {pin} pressed")
        pager = self.buttonPagerMap.get(pin)
        if pager:
            pager.togglePage()
    
    def update_leds(self):
        for pager in self.pagers:
            pager.greenLEDhandler()
    
    def shutdown(self):
        for pager in self.pagers:
            try:
                send_command("off", pager.ip)
            except Exception as e:
                print(f"Error sending shutdown to {pager.hostname}: {e}")
        GPIO.cleanup()


"""
To add a new pager to the network, simply create a new instance of the pager class in a variable, 
add it to the dictionary and list(found below) and the pager instance.
"""

# Logs data to a new row in the csv document
def logtocsv(data):
    file_exists = os.path.exists(CSV_FILE_NAME)
    
    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
        csv_writer= csv.writer(csvfile)
        
        if not file_exists:
            csv_writer.writerow(HEADER)
            print(f"Created new CSV file: {CSV_FILE_NAME} with header.")
            
        csv_writer.writerow(data)
        print(f"Logged: {data}")


# Sends a command over wifi to the target pager        
def send_command(command, target_ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((target_ip, PORT))
            s.sendall(command.encode())
            response = s.recv(1024)
            print(f"Send: '{command}', Received: '{response.decode()}'")
            return True if response else False
    except ConnectionRefusedError:
        print("Connection Refused.")
    except socket.timeout:
        print("Connection or Communication timed out")
    except Exception as e:
        print(f"Exception '{e}' occurred")
    return False

if __name__ == "__main__":
    pager_configs = [
        {"hostname": "knight1", "ip": "192.168.200.228", "button_pin": 7, "led_pin": 13},
        #Add more pagers here!
    ]
    
    manager = PagerNetworkManager(pager_configs)
    try:
        while True:
            manager.update_leds()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("shutdown")
        manager.shutdown()
    except Exception as e:
        print(f"Unexpected error: {e}")
 

