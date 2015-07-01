# -*- coding: utf8 -*-
from threading import Thread
import time

import RPi.GPIO as GPIO

from lcd import LCD, main as lcd_main
from traffic import Traffic, main as traffic_main
from rgb import RGB, main as rgb_main


class RunThread(Thread):
	def __init__(self, func):
		self.func = func
		return Thread.__init__(self)
	
	def run(self):
		while True:
			self.func()
			time.sleep(0.1)


def update_lcd(lcd):
	# Show the current time
	pass


def update_traffic(traffic):
	pass


def update_rgb(rgb):
	pass


def main():
	print 'Hello!'
	try:
		print 'Initialising...'
		GPIO.setmode(GPIO.BCM)
		lcd = LCD()
		traffic = Traffic(lcd=lcd, lcd_line=2)
		rgb = RGB(lcd=lcd, lcd_line=3)
		
		traffic_thread = RunThread(traffic.update)
		traffic_thread.start()
		
		print 'Testing everything...'
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
	#lcd_main()
	#traffic_main()
	#rgb_main()
	main()
