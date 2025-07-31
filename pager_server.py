import RPi.GPIO as GPIO
import time
from enum import Enum
from datetime import datetime
import csv
import time
import os
import sys
import socket

class Pager:
		
		paging = False
		
		def __init__(self, hostname, ip, buttonPin, LED):
			self.hostname = hostname
			self.ip = ip
			self.LED = LED
			self.buttonPin = buttonPin
			self.paging = False








HOST = '0.0.0.0' # this can stay 0.0.0.0
PORT = 65433 # The port the pagers are sending commands on

PAGER_LED_CONFIG = {
    "knight1": 11,
    

}



# Setting up the pager light
#GPIO.setup(r_pin, GPIO.OUT)
#GPIO.output(r_pin, GPIO.LOW)

# Enacts the command
def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    for pin in PAGER_LED_CONFIG.values():
        print(f"setup pin {pin}")
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def control_led(pager_name, state):
    pin = PAGER_LED_CONFIG.get(pager_name)
    if not pin:
        print(f"unknown pager requested, please add {pager_name} to the dictionary")
        return
        
    match state:
        case 'on':
            GPIO.output(r_pin, GPIO.HIGH)
        case 'off':
            GPIO.output(r_pin,GPIO.LOW)
        case _:
            GPIO.output(r_pin,GPIO.LOW)



def main():
    setup_gpio()
    
    try:
		# Listens to the given port, waiting for the client script to
		# Attempt to connect and send commands
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f'Pager server listening on port {PORT}')
            
            while True:
                conn, addr = s.accept()
                with conn:
                    print (f"Connected by {addr}")
                    while True:
                        
                        data = conn.recv(1024)
                        if not data:
                            break
                        command = data.decode().strip().lower()
                        if ':' in command:
                            pager_name, state = command.split(":", 1)
                            control_led(pager_name, state)
                            print(f"Received Command: '{command}'")
                            conn.sendall(b"Command Received")
                        else:
                            print(f"Malformed command: {command}")
                        
                
                
                 
        
        

                    
            
    except KeyboardInterrupt:
        print("server stopped by user.")
        
    except Exception as e:
        print(f"Error {e} occurred")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    
    main()
