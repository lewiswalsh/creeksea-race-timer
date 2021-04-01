import RPi.GPIO as GPIO
import lib4relay
import threading
import time
import csv

# Pins
BUTTON_ONE   = 23
BUTTON_TWO   = 24
BUTTON_RESET = 25
LED_READY    = 27
LED_RESET    = 17
LED_ONE      = 9
LED_TWO      = 10

# GPIO setup LED pins as outputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_READY, GPIO.OUT)
GPIO.setup(LED_RESET, GPIO.OUT)
GPIO.setup(LED_ONE, GPIO.OUT)
GPIO.setup(LED_TWO, GPIO.OUT)

# Set up and monitor a GPIO button
class Button(threading.Thread):
	def __init__(self, channel):
		threading.Thread.__init__(self)
		self._pressed = False # Assume Normally Open
		self.channel = channel
		GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set up pin as input
		self.daemon = True # Terminate thread when main program exits
		self.start() # Start thread running
	def pressed(self):
		if self._pressed:
			self._pressed = False # clear the pressed flag
			return True
		else:
			return False
	def run(self):
		previous = None
		while 1:
			current = GPIO.input(self.channel) # Read the GPIO channel
			time.sleep(0.05)
			# detect change from 1 to 0 (a button push)
			if current == False and previous == True:
				self._pressed = True
				# wait for flag to be cleared
				while self._pressed:
					time.sleep(0.05)
			previous = current


class Race(threading.Thread):
	def __init__(self, seq_fn):
		threading.Thread.__init__(self)
		self._sequence = {}
		self._seq_fn = seq_fn
		self._stop = False
		self.daemon = True
		self.start()

	# Stop sequence
	def stop(self):
		self._stop = True

	# Load sequence from CSV file
	def loadSequence(self):
		self._sequence = {}
		program = csv.reader(open(self._seq_fn))
		for row in program:
			if(len(row) > 0):
				bin = row[1] +""+ row[2] +""+ row[3] + row[4]
				self._sequence[int(row[0], 10)] = bin # int(bin, 2)
		return True

	# Run through sequence
	def countUp(self):
		end = max(self._sequence.iterkeys())
		for i in range(end):
			if self._stop:
				print("sequence stopped")
				break
			elif i in self._sequence:
				lib4relay.set_all(0, int(self._sequence[i], 2))
			time.sleep(1)
		self._stop = False
		init()

	# Load and run
	def run(self):
		self.loadSequence()
		self.countUp()


# Turn LED on or off
def lightLED(led, t):
	if t == -1: # Turn LED off
		GPIO.output(led, GPIO.LOW)
	else: # Turn LED on
		GPIO.output(led, GPIO.HIGH)
	if t > 0: # Turn off after t seconds
		time.sleep(t)
		GPIO.output(led, GPIO.LOW)


def flashLights():
	lightLED(LED_ONE, 0)
	lightLED(LED_TWO, 0)
	#lightLED(LED_READY, 0)
	lightLED(LED_RESET, 0)
	time.sleep(0.5)
	lightLED(LED_ONE, -1)
  lightLED(LED_TWO, -1)
  lightLED(LED_RESET, -1)


# Initialise program
def init():
	lightLED(LED_READY, -1)
	flashLights()
	lightLED(LED_READY, 0)


# Create Button instances
button_1 = Button(BUTTON_ONE)
button_2 = Button(BUTTON_TWO)
button_r = Button(BUTTON_RESET)

race = False
init()
while True: # Main program loop
	try:
		if button_1.pressed(): # Button for Seq. 1 pushed
			print("SEQUENCE ONE")
			lightLED(LED_ONE, 0)
			lightLED(LED_READY, -1)
			race = Race('./seq1.csv')
		if button_2.pressed(): # Button for Seq. 2 pushed
			print("SEQUENCE TWO")
			lightLED(LED_READY, -1)
			lightLED(LED_TWO, 0)
			race = Race('./seq2.csv')
		if button_r.pressed(): # Reset button pushed
			print("RESET")
			lightLED(LED_RESET, 1)
			if race:
				race.stop()
	except (KeyboardInterrupt, SystemExit): # Cleanup
		GPIO.cleanup()
		exit()


