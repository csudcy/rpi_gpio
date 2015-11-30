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

    # Indexes for colour lists
    R = 0
    G = 1
    B = 2
    A = 3

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
            [0, 0, 0, 0]
            for i in xrange(led_count)
        ]

        self.BITS_5 = self._generate_binary_array_lookup(5)
        self.BITS_8 = self._generate_binary_array_lookup(8)

        self.START_FRAME = [False] * 32
        self.PADDING_FRAME = [True] * 3
        self.END_FRAME = [True] * (led_count/2)

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

    def reset_leds(self):
        for led in self.LEDS:
            led[RGBStrip.R] = 0
            led[RGBStrip.G] = 0
            led[RGBStrip.B] = 0
            led[RGBStrip.A] = 0

    def set_led(self, index, r, g, b, a):
        led = self.LEDS[index]
        led[RGBStrip.R] = r
        led[RGBStrip.G] = g
        led[RGBStrip.B] = b
        led[RGBStrip.A] = a

    def get_led(self, index):
        return self.LEDS[index]

    def output(self):
        # 32 - Start frame of 0s
        self._output(self.START_FRAME)

        # Output each LED's values
        for led in self.LEDS:
            # 3 - Padding of 1s
            self._output(self.PADDING_FRAME)

            # 5 - Brightness
            self._output(self.BITS_5[led[RGBStrip.A]])

            # 8 - Blue
            self._output(self.BITS_8[led[RGBStrip.B]])

            # 8 - Green
            self._output(self.BITS_8[led[RGBStrip.G]])

            # 8 - Red
            self._output(self.BITS_8[led[RGBStrip.R]])

        # (LED_COUNT/2) - End frame of 1s
        self._output(self.END_FRAME)

    def _output(self, values):
        for value in values:
            # Set the data pin
            GPIO.output(self.PIN_DATA, value)

            # Cycle the clock
            GPIO.output(self.PIN_CLOCK, True)
            GPIO.output(self.PIN_CLOCK, False)


def test_rainbow(rgb_strip):
    index = 0
    while (True):
        # Output the LEDs
        #rgb_strip.reset_leds()
        rgb_strip.set_led((index +  5) % rgb_strip.LED_COUNT, 255,   0,   0, 1)
        rgb_strip.set_led((index +  4) % rgb_strip.LED_COUNT, 255, 255,   0, 1)
        rgb_strip.set_led((index +  3) % rgb_strip.LED_COUNT,   0, 255,   0, 1)
        rgb_strip.set_led((index +  2) % rgb_strip.LED_COUNT,   0, 255, 255, 1)
        rgb_strip.set_led((index +  1) % rgb_strip.LED_COUNT,   0,   0, 255, 1)
        rgb_strip.set_led((index +  0) % rgb_strip.LED_COUNT, 255,   0, 255, 1)
        rgb_strip.output()

        # Reset the first LED (all others will get changed again next time)
        rgb_strip.set_led((index +  0) % rgb_strip.LED_COUNT, 0, 0, 0, 0)

        # Move the LED along
        index = (index + 1) % rgb_strip.LED_COUNT

def test_clock(rgb_strip):
    last_hms = None
    while True:
        now = datetime.now()
        hms = (now.hour, now.minute, now.second)
        if hms != last_hms:
            print hms
            if last_hms is not None:
                # Clear previous time
                rgb_strip.set_led(last_hms[0], 0, 0, 0, 0)
                rgb_strip.set_led(last_hms[1], 0, 0, 0, 0)
                rgb_strip.set_led(last_hms[2], 0, 0, 0, 0)

            # Set new time
            rgb_strip.set_led(hms[0], 255, 0, 0, 1)
            led_m = rgb_strip.get_led(hms[1])
            rgb_strip.set_led(hms[1], led_m[0], led_m[1] + 255, led_m[2], 1)
            led_s = rgb_strip.get_led(hms[2])
            rgb_strip.set_led(hms[2], led_s[0], led_s[1], led_s[2] + 255, 1)

            # Update the output
            rgb_strip.output()

            # Save new time
            last_hms = hms
        time.sleep(0.1)

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

        print 'Testing rgb_strip...'
        # test_rainbow(rgb_strip)
        test_clock(rgb_strip)

    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        GPIO.cleanup()
    print 'Bye!'


if __name__ == '__main__':
    main()
