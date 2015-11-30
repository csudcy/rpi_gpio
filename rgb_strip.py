#!/usr/bin/python
# -*- coding: utf8 -*-
from collections import namedtuple
from datetime import datetime
import time

import RPi.GPIO as GPIO

from gpio_22 import GPIO22
from lcd import LCD

Color = namedtuple('Color', ('R', 'G', 'B', 'A'))


"""
TODO:
    Everything!
"""


class RGBStrip(object):
    """
    A simple interface for an APA102 RGB LED strip
    """

    def __init__(
            self,
            pin_data,
            pin_clock,
            led_count,
        ):
        self.PIN_DATA = pin_data
        self.PIN_CLOCK = pin_clock
        self.LED_COUNT = led_count
        self.LEDS = [
            Color(0, 0, 0, 0)
            for i in xrange(led_count)
        ]
        
        self.BITS_5 = self._generate_binary_array_lookup(5)
        self.BITS_8 = self._generate_binary_array_lookup(8)
 
        self._init_pins()
    
    def _generate_binary_array_lookup(self, bit_count):
        # Generate a lookup for 0-31 in 5 bit binary arrays
        return [
            [
                bit=='1'
                for bit in (bin(num)[2:]).zfill(bit_count)
            ]
            for num in xrange(2**bit_count)
        ]

    def _init_pins(self):
        GPIO.setup(
            self.PIN_DATA,
            GPIO.OUT,
        )
        GPIO.setup(
            self.PIN_CLOCK,
            GPIO.OUT,
        )
    
    def set_led(self, index, r, g, b, a):
        self.LEDS[index] = Color(r, g, b, a)

    def output(self):
        # 32 - Start frame of 0s
        GPIO.output(self.PIN_DATA, False)
        self._cycle_clock_multi(32)

        # Output each LED's values
        for led in self.LEDS:
            # 3 - Padding of 1s
            GPIO.output(self.PIN_DATA, True)
            self._cycle_clock_multi(32)

            # 5 - Brightness
            self._output(self.BITS_5[led.A])

            # 8 - Blue
            self._output(self.BITS_8[led.B])

            # 8 - Green
            self._output(self.BITS_8[led.G])

            # 8 - Red
            self._output(self.BITS_8[led.R])

        # (LED_COUNT/2) - End frame of 1s
        GPIO.output(self.PIN_DATA, True)
        self._cycle_clock_multi(self.LED_COUNT / 2)

    def _output(self, values):
        for value in values:
            # Set the data pin
            GPIO.output(self.PIN_DATA, value)

            # Cycle the clock
            GPIO.output(self.PIN_CLOCK, True)
            time.sleep(0.001)
            GPIO.output(self.PIN_CLOCK, False)
            time.sleep(0.001)

    def _cycle_clock_multi(self, count=1):
        for c in xrange(count):
            GPIO.output(self.PIN_CLOCK, True)
            time.sleep(0.001)
            GPIO.output(self.PIN_CLOCK, False)
            time.sleep(0.001)

def main():
    print 'Hello!'
    try:
        print 'Initialising...'
        GPIO.setmode(GPIO.BCM)
        rgb_strip = RGBStrip(
            pin_data=GPIO22.SCLK,
            pin_clock=GPIO22.MISO,
            led_count=60,
        )
 
        lcd = LCD(
            pin_rs=GPIO22.P7,
            pin_e=GPIO22.P6,
            pins_d=[
                GPIO22.P5,
                GPIO22.P4,
                GPIO22.P3,
                GPIO22.P2
            ],
        )

        print 'Testing rgb_strip...'
        index = 0
        while (True):
            # Show the current time
            lcd_time = datetime.now().strftime('%H:%M:%S    %d/%m/%y')
            lcd.output_line(lcd_time, 0)

            # Show the current index
            lcd.output_line(str(index), 1)

            # Move the LED along
            rgb_strip.set_led(index, 255, 0, 0, 31)
            time.sleep(0.001)
            rgb_strip.set_led(index, 0, 0, 0, 31)
            index = (index + 1) % rgb_strip.LED_COUNT
    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        GPIO.cleanup()
    print 'Bye!'


if __name__ == '__main__':
    main()
