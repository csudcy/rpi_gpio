#!/usr/bin/python
# -*- coding: utf8 -*-
import time

from RPi import GPIO

"""
TODO:
    Get if button is still depressed
"""


class Button(object):
    def __init__(
            self,
            pin,
        ):
        self.PIN = pin

        self._init_button()

    def _init_button(self):
        GPIO.setup(
            self.PIN,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN,
        )
        GPIO.add_event_detect(
            self.PIN,
            GPIO.RISING,
        )

    def was_pushed(self):
        return GPIO.event_detected(self.PIN)


def main():
    print 'Hello!'
    try:
        print 'Initialising...'
        GPIO.setmode(GPIO.BCM)
        button = Button(
            pin=11,
        )

        LED_OUT = 8
        GPIO.setup(LED_OUT, GPIO.OUT)

        print 'Testing button...'
        while (True):
            if button.was_pushed():
                print 'Pushed!'
                GPIO.output(LED_OUT, True)
            time.sleep(0.1)
            GPIO.output(LED_OUT, False)
    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        GPIO.cleanup()
    print 'Bye!'


if __name__ == '__main__':
    main()
