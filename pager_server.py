import RPi.GPIO as GPIO
import time
from enum import Enum
from datetime import datetime
import csv
import time
import os
import sys
import socket




GPIO.setmode(GPIO.BOARD) #Sets the pin numbering system to Board conventions




HOST = '0.0.0.0' # this can stay 0.0.0.0
PORT = 65433 # The port the pagers are sending commands on


r_pin = 11 # Board pin for the red LED to signal being paged
# Setting up the pager light
GPIO.setup(r_pin, GPIO.OUT)
GPIO.output(r_pin, GPIO.LOW)

# Enacts the command
def control_led(state):
    match state:
        case 'on':
            GPIO.output(r_pin, GPIO.HIGH)
        case 'off':
            GPIO.output(r_pin,GPIO.LOW)
        case _:
            GPIO.output(r_pin,GPIO.LOW)



def main():
    
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
                        print(f"Received Command: '{command}'")
                        control_led(command)
                        conn.sendall(b"Command Received")
                
                
                
        
        

                    
            
    except KeyboardInterrupt:
        print("server stopped by user.")
        
    except Exception as e:
        print(f"Error {e} occurred")
    finally:
        GPIO.cleanup()


main()
