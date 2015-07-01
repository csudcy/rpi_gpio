#!/usr/bin/python
# -*- coding: utf8 -*-
import time

import RPi.GPIO as GPIO

"""
TODO:
	Implement scrolling text
"""


class LCD(object):
	# Define some device constants
	LCD_CHR = True
	LCD_CMD = False
	
	# RAM address for output lines...
	LCD_LINES = [
		0x80,
		0xC0,
		0x94,
		0xD4
	]
	
	# Timing constants
	E_PULSE = 0.0005
	E_DELAY = 0.0005

	def __init__(
			self,
			pin_rs,
			pin_e,
			pins_d,
			width=20,
		):
		# Save the pins for later
		self.LCD_RS = pin_rs
		self.LCD_E = pin_e
		self.LCD_D4 = pins_d[0]
		self.LCD_D5 = pins_d[1]
		self.LCD_D6 = pins_d[2]
		self.LCD_D7 = pins_d[3]
		self.LCD_WIDTH = width
		
		self._init_pins()
		self._lcd_init()
	
	def output(self, lines):
		#if type(lines) == string:
		#	lines = lines.split('\n')
		# Make sure we blank all following lines
		while (len(lines) < 4):
			lines.append('')
		for i, line in enumerate(lines):
			self.output_line(line, i)
	
	def output_line(self, message, line_number):
		# Send string to display
		message = message.ljust(self.LCD_WIDTH," ")
		self._lcd_byte(self.LCD_LINES[line_number], self.LCD_CMD)		
		for i in range(self.LCD_WIDTH):
			self._lcd_byte(ord(message[i]), self.LCD_CHR)
	
	def _init_pins(self):
		# Setup all the pins as outputs
		GPIO.setup(self.LCD_RS, GPIO.OUT)
		GPIO.setup(self.LCD_E, GPIO.OUT)
		GPIO.setup(self.LCD_D4, GPIO.OUT)
		GPIO.setup(self.LCD_D5, GPIO.OUT)
		GPIO.setup(self.LCD_D6, GPIO.OUT)
		GPIO.setup(self.LCD_D7, GPIO.OUT)
	
	def _lcd_init(self):
		# Initialise display
		self._lcd_byte(0x33, self.LCD_CMD) # 110011 Initialise
		self._lcd_byte(0x32, self.LCD_CMD) # 110010 Initialise
		self._lcd_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction
		self._lcd_byte(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
		self._lcd_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size
		self._lcd_byte(0x01, self.LCD_CMD) # 000001 Clear display
		time.sleep(self.E_DELAY)
	
	def _lcd_byte(self, bits, mode):
		# Send byte to data pins
		# bits = data
		# mode = True  for character
		#        False for command
		
		GPIO.output(self.LCD_RS, mode) # RS
		
		# High bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(self.LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(self.LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(self.LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(self.LCD_D7, True)
		
		# Toggle 'Enable' pin
		self._lcd_toggle_enable()
		
		# Low bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(self.LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(self.LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(self.LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(self.LCD_D7, True)
		
		# Toggle 'Enable' pin
		self._lcd_toggle_enable()
	
	def _lcd_toggle_enable(self):
		# Toggle enable
		time.sleep(self.E_DELAY)
		GPIO.output(self.LCD_E, True)
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)
		time.sleep(self.E_DELAY)


def main():
	print 'Hello!'
	try:
		print 'Initialising...'
		GPIO.setmode(GPIO.BCM)
		lcd = LCD(
			pin_rs=4,
			pin_e=25,
			pins_d=[24,23,22,27],
		)
		
		print 'Testing LCD...'
		chr_code = 0
		lines = []
		while True:
			# Get 4 lines of output
			while (len(lines) < 4):
				output = ''
				for i in xrange(lcd.LCD_WIDTH):
					output += chr(chr_code)
					chr_code = (chr_code + 1) % 256
				lines.append(output)
			
			# Show the output
			lcd.output(lines)
			time.sleep(1)
			
			# Remove the first line
			lines = lines[1:]
	except KeyboardInterrupt:
		pass
	finally:
		print 'Cleaning up...'
		GPIO.cleanup()
	print 'Bye!'
	

if __name__ == '__main__':
	main()
