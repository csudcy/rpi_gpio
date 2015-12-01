#!/usr/bin/python
# -*- coding: utf8 -*-
from datetime import datetime
import random
import time

import RPi.GPIO as GPIO

from gpio_22 import GPIO22
from lcd import LCD


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

    def reset_leds(self, r=0, g=0, b=0, a=0):
        for led in self.LEDS:
            led[RGBStrip.R] = r
            led[RGBStrip.G] = g
            led[RGBStrip.B] = b
            led[RGBStrip.A] = a

    def set_led(self, index, r, g, b, a):
        led = self.LEDS[index % self.LED_COUNT]
        led[RGBStrip.R] = int(r)
        led[RGBStrip.G] = int(g)
        led[RGBStrip.B] = int(b)
        led[RGBStrip.A] = int(a)

    def add_led(self, index, r=0, g=0, b=0, a=0):
        led = self.LEDS[index % self.LED_COUNT]
        led[RGBStrip.R] = min(led[RGBStrip.R] + int(r), 255)
        led[RGBStrip.G] = min(led[RGBStrip.G] + int(g), 255)
        led[RGBStrip.B] = min(led[RGBStrip.B] + int(b), 255)
        led[RGBStrip.A] = min(led[RGBStrip.A] + int(a), 255)

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


def test_brightness(rgb_strip):
    """
    Test what different brightness & RGB levels look like
    """
    COLOURS = (
        (255,   0,   0),
        (255, 255,   0),
        (  0, 255,   0),
        (  0, 255, 255),
        (  0,   0, 255),
        (255,   0, 255),
    )
    COLOUR = 0
    while (True):
        # Get the current colour and move to the next colour
        COLOUR_R, COLOUR_G, COLOUR_B = COLOURS[COLOUR]
        COLOUR = (COLOUR + 1) % len(COLOURS)

        rgb_strip.set_led(0, COLOUR_R, COLOUR_G, COLOUR_B, 31)
        rgb_strip.set_led(1, COLOUR_R, COLOUR_G, COLOUR_B, 23)
        rgb_strip.set_led(2, COLOUR_R, COLOUR_G, COLOUR_B, 15)
        rgb_strip.set_led(3, COLOUR_R, COLOUR_G, COLOUR_B, 7)
        rgb_strip.set_led(4, COLOUR_R, COLOUR_G, COLOUR_B, 1)
        rgb_strip.set_led(5, COLOUR_R, COLOUR_G, COLOUR_B, 0)

        rgb_strip.set_led(7, COLOUR_R*1.0, COLOUR_G*1.0, COLOUR_B*1.0, 31)
        rgb_strip.set_led(8, COLOUR_R*0.8, COLOUR_G*0.8, COLOUR_B*0.8, 31)
        rgb_strip.set_led(9, COLOUR_R*0.6, COLOUR_G*0.6, COLOUR_B*0.6, 31)
        rgb_strip.set_led(10, COLOUR_R*0.4, COLOUR_G*0.4, COLOUR_B*0.4, 31)
        rgb_strip.set_led(11, COLOUR_R*0.2, COLOUR_G*0.2, COLOUR_B*0.2, 31)
        rgb_strip.set_led(12, COLOUR_R/255, COLOUR_G/255, COLOUR_B/255, 31)

        rgb_strip.set_led(14, COLOUR_R*1.0, COLOUR_G*1.0, COLOUR_B*1.0, 1)
        rgb_strip.set_led(15, COLOUR_R*0.8, COLOUR_G*0.8, COLOUR_B*0.8, 1)
        rgb_strip.set_led(16, COLOUR_R*0.6, COLOUR_G*0.6, COLOUR_B*0.6, 1)
        rgb_strip.set_led(17, COLOUR_R*0.4, COLOUR_G*0.4, COLOUR_B*0.4, 1)
        rgb_strip.set_led(18, COLOUR_R*0.2, COLOUR_G*0.2, COLOUR_B*0.2, 1)
        rgb_strip.set_led(19, COLOUR_R/255, COLOUR_G/255, COLOUR_B/255, 1)

        rgb_strip.output()

        time.sleep(1)


def test_rainbow_train(rgb_strip):
    """
    Make 6 colours move along the strip & cycle round
    """
    index = 0
    while (True):
        # Output the LEDs
        rgb_strip.set_led((index +  5) % rgb_strip.LED_COUNT, 255,   0,   0, 31)
        rgb_strip.set_led((index +  4) % rgb_strip.LED_COUNT, 255, 255,   0, 31)
        rgb_strip.set_led((index +  3) % rgb_strip.LED_COUNT,   0, 255,   0, 31)
        rgb_strip.set_led((index +  2) % rgb_strip.LED_COUNT,   0, 255, 255, 31)
        rgb_strip.set_led((index +  1) % rgb_strip.LED_COUNT,   0,   0, 255, 31)
        rgb_strip.set_led((index +  0) % rgb_strip.LED_COUNT, 255,   0, 255, 31)
        rgb_strip.output()

        # Reset the first LED (all others will get changed again next time)
        rgb_strip.set_led((index +  0) % rgb_strip.LED_COUNT, 0, 0, 0, 0)

        # Move the LED along
        index = (index + 1) % rgb_strip.LED_COUNT


def get_rgb_rainbow(count, max_rgb=127):
    # Thanks to http://stackoverflow.com/questions/876853/generating-color-ranges-in-python
    import colorsys
    HSV_tuples = [
        (x*1.0/count, 1, 1)
        for x in range(count)
    ]
    RGB_tuples = [
        [
            hsv * max_rgb
            for hsv in colorsys.hsv_to_rgb(*hsv)
        ]
        for hsv in HSV_tuples
    ]

    return RGB_tuples


def test_rainbow(rgb_strip):
    """
    Make the whole strip into a cycling rainbow
    """
    # Work out a rainbow for #LED_COUNT leds
    COLOURS = get_rgb_rainbow(rgb_strip.LED_COUNT)

    index = 0
    while (True):
        # Output the LEDs
        for i in xrange(rgb_strip.LED_COUNT):
            rgb_strip.set_led((index +  i) % rgb_strip.LED_COUNT, *COLOURS[i], a=1)
        rgb_strip.output()

        # Move the LED along
        index = (index + 1) % rgb_strip.LED_COUNT


def test_clock(rgb_strip):
    """
    A clock! Hours=Red, Minutes=Green, Seconds=Blue
    """
    last_hms = None
    while True:
        now = datetime.now()
        hms = (now.hour, now.minute, now.second)
        if hms != last_hms:
            # Clear all the LEDs
            rgb_strip.reset_leds(a=1)

            # Set new time
            rgb_strip.add_led(hms[0]-1, r= 32)
            rgb_strip.add_led(hms[0]  , r=255)
            rgb_strip.add_led(hms[0]+1, r= 32)
            rgb_strip.add_led(hms[1]-1, g= 32)
            rgb_strip.add_led(hms[1]  , g=255)
            rgb_strip.add_led(hms[1]+1, g= 32)
            rgb_strip.add_led(hms[2]-1, b= 32)
            rgb_strip.add_led(hms[2]  , b=255)
            rgb_strip.add_led(hms[2]+1, b= 32)

            # Update the output
            rgb_strip.output()

            # Save new time
            last_hms = hms
        time.sleep(0.1)


def test_gravity(rgb_strip):
    """
    Shoot colours from one end and watch gravity pull them back down
    """
    COLOURS = get_rgb_rainbow(10)
    SHOTS = []
    MIN_SPEED = 0.5
    MAX_SPEED = 1.0
    G_SPEED = MAX_SPEED / (rgb_strip.LED_COUNT * 2)
    print 'MAX_SPEED = {MAX_SPEED}'.format(MAX_SPEED=MAX_SPEED)
    print 'LED_COUNT = {LED_COUNT}'.format(LED_COUNT=rgb_strip.LED_COUNT)
    print 'G_SPEED   = {G_SPEED}'.format(G_SPEED=G_SPEED)

    while True:
        # Simulate existing shots
        for shot in SHOTS:
            # Update position
            shot['position'] += shot['speed']
            # Update speed
            shot['speed'] -= G_SPEED

        # Remove old shots
        SHOTS = [
            shot
            for shot in SHOTS
            if shot['position'] > 0
        ]

        # Add a new shot?
        if random.random() < 0.2 / (len(SHOTS) + 1):
            print 'Adding a shot! {count} existing'.format(count=len(SHOTS))
            SHOTS.append({
                'colour': random.choice(COLOURS),
                'speed': random.uniform(MIN_SPEED, MAX_SPEED),
                'position': 0.0
            })

        # Clear all the LEDs
        rgb_strip.reset_leds(a=1)

        # Show all the shots
        for shot in SHOTS:
            rgb_strip.add_led(
                int(shot['position']),
                *shot['colour']
            )

        # Update the output
        rgb_strip.output()


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
        #test_rainbow_train(rgb_strip)
        #test_clock(rgb_strip)
        #test_brightness(rgb_strip)
        #test_rainbow(rgb_strip)
        test_gravity(rgb_strip)

    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        GPIO.cleanup()
    print 'Bye!'


if __name__ == '__main__':
    main()
