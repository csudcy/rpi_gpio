#!/usr/bin/python
# -*- coding: utf8 -*-
from datetime import datetime
import time

import RPi.GPIO as GPIO

from button import Button
from lcd import LCD
from rgb import RGB
from traffic import Traffic

class Super(object):
    def __init__(self):
        self.BUTTON = Button(
            pin=11,
        )
        GPIO.setup(
            self.WAITING_PIN,
            GPIO.OUT,
        )

        self.LCD = LCD(
            pin_rs=4,
            pin_e=25,
            pins_d=[24,23,22,27],
        )

        self.TRAFFIC = Traffic(
            pin_red=14,
            pin_amber=3,
            pin_green=2,
            lcd=self.LCD,
            lcd_line=2,
        )

        self.RGB = RGB(
            pin_red=9,
            pin_green=10,
            pin_blue=15,
            lcd=self.LCD,
            lcd_line=3,
        )
        self.RGB.show_colour(self.RGB_MAX, self.RGB_MIN, self.RGB_MIN)

    def update(self):
        self._update_lcd()
        self._update_button()
        self._update_traffic()
        self._update_rgb()

    LCD_LAST_TIME = ''
    def _update_lcd(self):
        # Show the current time
        lcd_time = datetime.now().strftime('%H:%M:%S    %d/%m/%y')
        if lcd_time != self.LCD_LAST_TIME:
            self.LCD_LAST_TIME = lcd_time
            self.LCD.output_line(lcd_time, 0)

    WAITING_PIN = 8
    PREV_WAIT_STATE = None
    def _update_button(self):
        if self.BUTTON.was_pushed():
            self.TRAFFIC.push_the_button()

        wait_state = self.TRAFFIC.is_waiting
        if wait_state != self.PREV_WAIT_STATE:
            if wait_state:
                self.LCD.output_line('Waiting...', 1)
            else:
                self.LCD.output_line('', 1)
            GPIO.output(
                self.WAITING_PIN,
                wait_state,
            )
            self.PREV_WAIT_STATE = wait_state

    def _update_traffic(self):
        # Make the traffic lights work
        self.TRAFFIC.update()

    RGB_MIN = 0.0
    RGB_MAX = 100.0
    RGB_STEP = 0
    RGB_STEPS = (
        (RGB_MAX, RGB_MIN, RGB_MIN),
        (RGB_MAX, RGB_MAX, RGB_MIN),
        (RGB_MIN, RGB_MAX, RGB_MIN),
        (RGB_MIN, RGB_MAX, RGB_MAX),
        (RGB_MIN, RGB_MIN, RGB_MAX),
        (RGB_MAX, RGB_MIN, RGB_MAX),
    )
    def _update_rgb(self):
        # Make a rainbow
        # If the current step is finished, move to the next
        if not self.RGB.goto_colour_active:
            # Show the next step
            self.RGB_STEP = (self.RGB_STEP + 1) % len(self.RGB_STEPS)
            self.RGB.goto_colour(*self.RGB_STEPS[self.RGB_STEP])

        # But always update
        self.RGB.update()


def main():
    print 'Hello!'
    try:
        print 'Initialising...'
        GPIO.setmode(GPIO.BCM)
        super = Super()

        print 'Testing everything...'
        while True:
            super.update()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        GPIO.cleanup()
    print 'Bye!'



if __name__ == '__main__':
    main()
