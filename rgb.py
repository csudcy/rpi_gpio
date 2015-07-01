#!/usr/bin/python
# -*- coding: utf8 -*-
from collections import namedtuple
import time

import RPi.GPIO as GPIO

from lcd import LCD

Color = namedtuple('Color', ('R', 'G', 'B'))

"""
TODO:
	Use Color tuples everywhere
"""


class RGB(object):
	PWM_FREQ = 500
	
	def __init__(
			self,
			pin_red,
			pin_green,
			pin_blue,
			lcd=None,
			lcd_line=None,
		):
		self.LED_R = pin_red
		self.LED_G = pin_green
		self.LED_B = pin_blue
		self.LCD = lcd
		self.LCD_LINE = lcd_line
		
		self.GOTO_ACTIVE = False
		
		self._init_pins()
	
	def _init_pins(self):
		# Setup all the pins as outputs
		GPIO.setup(self.LED_R, GPIO.OUT)
		GPIO.setup(self.LED_G, GPIO.OUT)
		GPIO.setup(self.LED_B, GPIO.OUT)
		
		# Setup the PWM threads
		self.PWM_R = GPIO.PWM(self.LED_R, self.PWM_FREQ)
		self.PWM_G = GPIO.PWM(self.LED_G, self.PWM_FREQ)
		self.PWM_B = GPIO.PWM(self.LED_B, self.PWM_FREQ)
		
		# Start everything off
		self.PWM_R.start(0)
		self.PWM_G.start(0)
		self.PWM_B.start(0)
	
	def show_colour(self, r, g, b):
		# We are directly setting a colour
		# Disabl any active goto_colour call
		self.GOTO_ACTIVE = False
		self._set_colour(r, g, b)
	
	@property
	def goto_colour_active(self):
		return self.GOTO_ACTIVE
	
	def goto_colour(self, r, g, b, seconds=1):
		self.GOTO_ACTIVE = True
		self.GOTO_SECONDS = seconds
		self.GOTO_START_R = self.CURRENT_R
		self.GOTO_START_G = self.CURRENT_G
		self.GOTO_START_B = self.CURRENT_B
		self.GOTO_DIFF_R = r - self.CURRENT_R
		self.GOTO_DIFF_G = g - self.CURRENT_G
		self.GOTO_DIFF_B = b - self.CURRENT_B
		self.GOTO_START_TIME = time.time()
	
	def update(self):
		# If there is an active goto_colour, update it	
		if self.GOTO_ACTIVE:
			elapsed_time = time.time() - self.GOTO_START_TIME
			elapsed_ratio = elapsed_time / self.GOTO_SECONDS	
			if elapsed_ratio > 1.0:
				# We have finished the goto_colour
				self.GOTO_ACTIVE = False
				elapsed_ratio = 1.0
			self._set_colour(
				self.GOTO_START_R + self.GOTO_DIFF_R * elapsed_ratio,
				self.GOTO_START_G + self.GOTO_DIFF_G * elapsed_ratio,
				self.GOTO_START_B + self.GOTO_DIFF_B * elapsed_ratio,
			)

	def _set_colour(self, r, g, b):
		#0.0 <= r, g, b <= 100.0
		if self.LCD:
			self.LCD.output_line(
				'(R:{r: >3.0f} G:{g: >3.0f} B:{b: >3.0f})'.format(
					r=r,
					g=g,
					b=b,
				),
				self.LCD_LINE
			)
		#print r, g, b
		self.CURRENT_R = r
		self.CURRENT_G = g
		self.CURRENT_B = b
		self.PWM_R.ChangeDutyCycle(r)
		self.PWM_G.ChangeDutyCycle(g)
		self.PWM_B.ChangeDutyCycle(b)


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
		rgb = RGB(
			pin_red=9,
			pin_green=10,
			pin_blue=15,
			lcd=lcd,
			lcd_line=0,
		)
		
		print 'Testing rgb...'
		COLOR_MIN = 0.0
		COLOR_MAX = 100.0
		rgb.show_colour(COLOR_MAX, COLOR_MIN, COLOR_MIN)

		def goto_and_wait(r, g, b):
			rgb.goto_colour(r, g, b)
			while rgb.goto_colour_active:
				time.sleep(0.001)
				rgb.update()

		while True:
			goto_and_wait(COLOR_MAX, COLOR_MAX, COLOR_MIN)
			goto_and_wait(COLOR_MIN, COLOR_MAX, COLOR_MIN)
			goto_and_wait(COLOR_MIN, COLOR_MAX, COLOR_MAX)
			goto_and_wait(COLOR_MIN, COLOR_MIN, COLOR_MAX)
			goto_and_wait(COLOR_MAX, COLOR_MIN, COLOR_MAX)
			goto_and_wait(COLOR_MAX, COLOR_MIN, COLOR_MIN)
	except KeyboardInterrupt:
		pass
	finally:
		print 'Cleaning up...'
		GPIO.cleanup()
	print 'Bye!'
	

if __name__ == '__main__':
	main()
