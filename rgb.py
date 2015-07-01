# -*- coding: utf8 -*-
import time

import RPi.GPIO as GPIO

from lcd import LCD


class RGB(object):
	PWM_FREQ = 500
	
	def __init__(self, pin_red=9, pin_green=10, pin_blue=15, lcd=None, lcd_line=0):
		self.LED_R = pin_red
		self.LED_G = pin_green
		self.LED_B = pin_blue
		self.LCD = lcd
		self.LCD_LINE = lcd_line
		
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
	
	def goto_colour(self, r, g, b, seconds=1, time_step=0.01):
		start_r = self.CURRENT_R
		start_g = self.CURRENT_G
		start_b = self.CURRENT_B
		diff_r = r - self.CURRENT_R
		diff_g = g - self.CURRENT_G
		diff_b = b - self.CURRENT_B
		start_time = time.time()
		while True:
			elapsed_time = time.time() - start_time
			if elapsed_time >= seconds:
				break
			
			elapsed_ratio = elapsed_time / seconds	
			
			self.show_colour(
				start_r + diff_r * elapsed_ratio,
				start_g + diff_g * elapsed_ratio,
				start_b + diff_b * elapsed_ratio,
			)
			time.sleep(time_step)
		self.show_colour(r, g, b)

def main():
	print 'Hello!'
	try:
		print 'Initialising...'
		GPIO.setmode(GPIO.BCM)
		lcd = LCD()
		rgb = RGB(lcd=lcd, lcd_line=3)
		
		print 'Testing rgb...'
		COLOR_MIN = 0.0
		COLOR_MAX = 100.0
		rgb.show_colour(COLOR_MAX, COLOR_MIN, COLOR_MIN)
		while True:
			rgb.goto_colour(COLOR_MAX, COLOR_MAX, COLOR_MIN)
			rgb.goto_colour(COLOR_MIN, COLOR_MAX, COLOR_MIN)
			rgb.goto_colour(COLOR_MIN, COLOR_MAX, COLOR_MAX)
			rgb.goto_colour(COLOR_MIN, COLOR_MIN, COLOR_MAX)
			rgb.goto_colour(COLOR_MAX, COLOR_MIN, COLOR_MAX)
			rgb.goto_colour(COLOR_MAX, COLOR_MIN, COLOR_MIN)
	except KeyboardInterrupt:
		pass
	finally:
		print 'Cleaning up...'
		GPIO.cleanup()
	print 'Bye!'
	

if __name__ == '__main__':
	main()
