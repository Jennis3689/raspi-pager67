try:

	import RPi.GPIO as GPIO
	import socket
	import time
	from enum import Enum
	from datetime import datetime
	import csv
	import time
	import os

	class Pager:
		
		global pagingStatus
		paging = False
		turnedofftime = None
		turnedontime = None
		elapsedtime = None
		fturnedofftime = None
		fturnedontime = None
		thisLED = False 
		
		def __init__(self, hostname, ip, buttonPin, LED):
			self.hostname = hostname
			self.ip = ip
			self.LED = LED
			self.buttonPin = buttonPin
			self.paging = False
			
		def togglePage(self):
			
			
			if self.paging:
				if send_command("off", self.ip):
					self.paging = not self.paging
					self.collectTime(True)
					pagingStatus[self] = not pagingStatus[self]
			else:
				if send_command("on", self.ip):
					self.paging = not self.paging
					self.collectTime(False)
					pagingStatus[self] = not pagingStatus[self]
		
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

	"""
	To add a new pager to the network, simply create a new instance of the pager class in a variable, 
	add it to the dictionary and list(found below) and the pager instance.
	"""

	#PAGER VARIABLES

	# boardname = Pager("hostname", "ip address", button to page this board as an integer)
	knight1 = Pager("knight1", "192.168.200.227", 7, 13)


	# buttonPagerPairs = {button:instance of pager, button2:instance of pager2, ...}
	buttonPagerPairs = {7:knight1}
	# listOfPagers = [pager1, pager2, pager3]
	listOfPagers = [knight1]

	pagingStatus = dict.fromkeys(listOfPagers, False)

	# Global Variables for the CSV page logging
	CSV_FILE_NAME = "pager_log.csv"
	HEADER = ["Target", "Turned On", "Turned Off", "Time Elapsed"]



	# Port used for the sending of commands to other raspi's
	PORT = 65433

	# Use the board pin numbering convention
	GPIO.setmode(GPIO.BOARD)

	gPin = 13 # The pin for the green light of this pager to light when the board is actively paging another board.


	# Logs  data to a new row in the csv document
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
				if response is None:
					return send_command(command, target_ip)
				else:
					return True
		except ConnectionRefusedError:
			print("Connection Refused.")
		except socket.timeout:
			print("Connection or Communication timed out")
		except Exception as e:
			print(f"Exception '{e}' occurred")


	def buttonPressHandler(c):
		print("Button Pressed")
		pager = buttonPagerPairs[c]
		pager.togglePage()
		
		
				
	#Make sure to add all instances of the pager class as a global variable inside main like the example



	def main():
		listener = True
		#global pagerVariable
		global knight1
		
		
		for i in buttonPagerPairs:
			GPIO.setup(i, GPIO.IN)
			GPIO.add_event_detect(i, GPIO.BOTH, callback = buttonPressHandler, bouncetime=300)
		
		while True:
		   
			for i in listOfPagers:
				GPIO.setup(i.LED, GPIO.OUT)
				i.greenLEDhandler()	
			
			time.sleep(0.1)
			
	main()
 
except Exception as e:
	try:
		for i in listOfPagers:
			send_command('off', i.ip)
	except Exception as e:
		print(f"{e} occurred")
	finally:
		GPIO.cleanup()
		print(f"{e} occurred")

