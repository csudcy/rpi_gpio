import time

from RPi import GPIO

RED_LED = 14
AMBER_LED = 3
GREEN_LED = 2

RED_STATE = True
AMBER_STATE = False
GREEN_STATE = False

print 'Setup...'
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(AMBER_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)

try:
	print 'Flashing...'
	while (True):
		GPIO.output(RED_LED, RED_STATE)
		GPIO.output(AMBER_LED, AMBER_STATE)
		GPIO.output(GREEN_LED, GREEN_STATE)
		time.sleep(1)
		RED_STATE, AMBER_STATE, GREEN_STATE = GREEN_STATE, RED_STATE, AMBER_STATE
except KeyboardInterrupt, ex:
	pass
finally:
	print 'Cleaning up...'
	#lcd_byte(0x01, LCD_CMD)
	#lcd_string("Goodbye!",LCD_LINE_1)
	GPIO.cleanup()

print 'Done!'
