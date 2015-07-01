import time

from RPi import GPIO

BUTTON_INPUT = 11
LED_OUT = 8

print 'Setup...'
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_OUT, GPIO.OUT)
GPIO.add_event_detect(BUTTON_INPUT, GPIO.RISING)

try:
        print 'Reading...'
        while (True):
                if GPIO.event_detected(BUTTON_INPUT):
			print 'Pushed!'
			GPIO.output(LED_OUT, True)
                time.sleep(1)
		GPIO.output(LED_OUT, False)
except KeyboardInterrupt, ex:
        pass
finally:
        print 'Cleaning up...'
        GPIO.cleanup()

print 'Done!'
