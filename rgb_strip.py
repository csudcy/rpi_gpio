#!/usr/bin/python
# -*- coding: utf8 -*-
from collections import namedtuple
from datetime import datetime
import math
import random
import time

import RPi.GPIO as GPIO

from gpio_22 import GPIO22
from lcd import LCD

"""
To use SPI mode:
    * sudo apt-get update
    * sudo apt-get upgrade
    * sudo raspi-config
        * Advanced options
        * SPI
        * Enable
    * sudo pip install spidev
*Note:* It seems like SPI mode cannot be used if any of the pins have been used by GPIO (reboot to fix).

TODO:
    Everything!
    Make RainbowTrain loop instead of jumping back to x=0 every line
"""


class RGBStrip(object):
    """
    A simple interface for an APA102 RGB LED strip
    """

    def __init__(
            self,
            led_count=None,
            width=None,
            height=None,
            pin_data=None,
            pin_clock=None,
        ):
        """
        Note: To enable SPI mode, omit pin_data and pin_clock
        """
        if width:
            self.WIDTH = width
            self.HEIGHT = height
        else:
            self.WIDTH = led_count
            self.HEIGHT = 1

        self.LED_COUNT = width * height

        # Work out some byte counts
        self.BYTES_START = 4
        self.BYTES_LED = self.LED_COUNT * 4
        end_bit_count = self.LED_COUNT / 2.0
        self.BYTES_END = int(math.ceil(end_bit_count / 8.0))
        self.BYTES_TOTAL = self.BYTES_START + self.BYTES_LED + self.BYTES_END

        # Setup the byte array that we will output
        self.BYTES = [None] * self.BYTES_TOTAL

        # Setup the start & end frames
        self.BYTES[:self.BYTES_START] = [0x00] * self.BYTES_START
        self.BYTES[-self.BYTES_END:] = [0xFF] * self.BYTES_END

        # Setup the LED frames so the padding bits are set correctly
        self.set_leds()

        # Where to write the data to (depending on our mode)
        self.SPI = None
        self.PIN_DATA = None
        self.PIN_CLOCK = None

        # Setup stuff based on what mode we're running in
        if pin_data is None:
            self._init_spi()
        else:
            self._init_pins(pin_data, pin_clock)

        # Setup a list of renderers
        self.RENDERERS = set()

    def _init_spi(self):
        # Init the SPI bus
        import spidev
        self.SPI = spidev.SpiDev()
        self.SPI.open(
            0, #bus
            0, #device
        )
        self.SPI.max_speed_hz = 16 * 1000 * 1000

    def _init_pins(self, pin_data, pin_clock):
        self.PIN_DATA = pin_data
        self.PIN_CLOCK = pin_clock

        # Prepare lookup table
        self.BITS_8 = self._generate_binary_array_lookup(8)

        # Setup GPIO
        GPIO.setup(
            self.PIN_DATA,
            GPIO.OUT,
        )
        GPIO.setup(
            self.PIN_CLOCK,
            GPIO.OUT,
        )

    def _generate_binary_array_lookup(self, bit_count):
        # Generate a lookup for 0-2**bit_count in bit_count bit binary arrays
        return [
            [
                bit=='1'
                for bit in (bin(num)[2:]).zfill(bit_count)
            ]
            for num in xrange(2**bit_count)
        ]

    def _get_offset(self, index):
        return self.BYTES_START + index * 4

    def _get_index(self, x, y):
        return (y * self.WIDTH) + (x if y % 2 == 0 else self.WIDTH - x - 1)

    def set_leds(self, r=0, g=0, b=0, a=0):
        for offset in xrange(self.BYTES_START, self.BYTES_START + self.BYTES_LED, 4):
            self._set_led(
                offset,
                r,
                g,
                b,
                a
            )

    def set_led(self, index, r=0, g=0, b=0, a=0):
        offset = self._get_offset(index)
        self._set_led(
            self._get_offset(index),
            r,
            g,
            b,
            a
        )

    def set_led_xy(self, x, y, r=0, g=0, b=0, a=0):
        index = self._get_index(x, y)
        self.set_led(index, r, g, b, a)

    def add_led(self, index, r=0, g=0, b=0, a=0):
        offset = self._get_offset(index)
        self._set_led(
            self._get_offset(index),
            self.BYTES[offset + 3] + r,
            self.BYTES[offset + 2] + g,
            self.BYTES[offset + 1] + b,
            self.BYTES[offset + 0] + a
        )

    def add_led_xy(self, x, y, r=0, g=0, b=0, a=0):
        index = self._get_index(x, y)
        self.add_led(index, r, g, b, a)

    def _set_led(self, offset, r, g, b, a):
        # Brightness max is 31; or with 224 to add the padding 1s
        self.BYTES[offset + 0] = (int(a) & 31) | 224
        # R, G, B are max 255
        self.BYTES[offset + 1] = int(b) & 255
        self.BYTES[offset + 2] = int(g) & 255
        self.BYTES[offset + 3] = int(r) & 255

    def add_renderer(self, renderer):
        self.RENDERERS.add(renderer)

    def render(self):
        """
        Clear all LEDs, render all renderers then output the results
        """
        self.set_leds()
        for renderer in self.RENDERERS:
            renderer.render()
        self.output()

    def render_forever(self, sleep_time=0.01):
        while (True):
            self.render()
            time.sleep(sleep_time)

    def output(self):
        if self.SPI:
            self._output_spi()
        else:
            self._output_pins()

    def _output_spi(self):
        self.SPI.writebytes(self.BYTES)

    def _output_pins(self):
        for byte in self.BYTES:
            bits = self.BITS_8[byte]
            for bit in bits:
                # Set the data pin
                GPIO.output(self.PIN_DATA, bit)

                # Cycle the clock
                GPIO.output(self.PIN_CLOCK, True)
                GPIO.output(self.PIN_CLOCK, False)

    @staticmethod
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


StripSection = namedtuple('StripSection', ('id', 'rgb_strip', 'x', 'y'))

class RainbowTrainRenderer(object):
    def __init__(self, width, height=1, train_length=10, max_rgb=127):
        self.width = width
        self.height = height

        self.outputs = []
        self.COLOURS = RGBStrip.get_rgb_rainbow(train_length, max_rgb=max_rgb)
        self.x = 0
        self.y = 0

    def add_output(self, id, rgb_strip, x, y=1):
        # Save this in my list of outputs
        self.outputs.append(StripSection(
            id,
            rgb_strip,
            x,
            y
        ))

        # Register myself with the rgb_strip so I will get rendered & output
        rgb_strip.add_renderer(self)

    def xy_inc(self, x, y, w, h):
        # Move to the next column
        x += 1
        if x >= w:
            # Move to the next row
            x = 0
            y += 1
            if y >= h:
                y = 0
        return x, y

    def render(self):
        for output in self.outputs:
            # Clear the LEDs
            for x in xrange(output.x, output.x + self.width):
                for y in xrange(output.y, output.y + self.height):
                    #print 'Clr', output.id, x, y
                    output.rgb_strip.set_led_xy(x, y)

            # Output the colours
            x, y = self.x, self.y
            for i, colour in enumerate(self.COLOURS):
                x, y = self.xy_inc(x, y, self.width, self.height)
                #print 'Out', output.id, x, y, output.x + x, output.y + y, self.width, self.height
                output.rgb_strip.set_led_xy(output.x + x, output.y + y, *colour, a=1)

        # Move the train along
        self.x, self.y = self.xy_inc(self.x, self.y, self.width, self.height)


def test_brightness(rgb_strip):
    """
    Test what different brightness & RGB levels look like
    """
    COLOURS = RGBStrip.get_rgb_rainbow(6, max_rgb=255)
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
    Make a small rainbow move along the strip & cycle round
    """
    rt = RainbowTrainRenderer(rgb_strip.WIDTH, rgb_strip.HEIGHT, 10)
    rt.add_output('RT', rgb_strip, 0, 0)
    rgb_strip.render_forever()


def test_rainbow(rgb_strip):
    """
    Make the whole strip into a cycling rainbow
    """
    rt = RainbowTrainRenderer(rgb_strip.WIDTH, rgb_strip.HEIGHT, rgb_strip.WIDTH * rgb_strip.HEIGHT)
    rt.add_output('RT', rgb_strip, 0, 0)
    rgb_strip.render_forever()


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
            rgb_strip.set_leds(a=1)

            # Set new time
            for y in xrange(rgb_strip.HEIGHT):
                rgb_strip.add_led_xy(hms[0], y, r=255)
                rgb_strip.add_led_xy(hms[1], y, g=255)
                rgb_strip.add_led_xy(hms[2], y, b=255)

            # Update the output
            rgb_strip.output()

            # Save new time
            last_hms = hms
        time.sleep(0.1)


def test_gravity(rgb_strip):
    """
    Shoot colours from one end and watch gravity pull them back down
    """
    COLOURS = RGBStrip.get_rgb_rainbow(10)
    SHOTS = []
    MIN_SPEED = 0.5
    MAX_SPEED = 1.0
    G_SPEED = MAX_SPEED / (rgb_strip.WIDTH * 2)
    print 'MAX_SPEED = {}'.format(MAX_SPEED)
    print 'WIDTH     = {}'.format(rgb_strip.WIDTH)
    print 'G_SPEED   = {}'.format(G_SPEED)

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
        rgb_strip.set_leds(a=1)

        # Show all the shots
        for shot in SHOTS:
            for y in xrange(rgb_strip.HEIGHT):
                rgb_strip.add_led_xy(
                    int(shot['position']),
                    y,
                    *shot['colour']
                )

        # Update the output
        rgb_strip.output()

        time.sleep(0.02)


def test_many(rgb_strip):
    rt1 = RainbowTrainRenderer(30, 2, 60)
    rt1.add_output('RT1  ', rgb_strip, 0, 0)

    rt2 = RainbowTrainRenderer(30, 1)
    rt2.add_output('RT2 T', rgb_strip, 30, 0)
    rt2.add_output('RT2 B', rgb_strip, 30, 1)
    while (True):
        rgb_strip.render()
        time.sleep(0.01)


def main():
    print 'Hello!'
    rgb_strip = None
    try:
        print 'Initialising...'
        GPIO.setmode(GPIO.BCM)
        rgb_strip = RGBStrip(
            #led_count=120,
            width=60,
            height=2,
            #pin_data=GPIO22.MOSI,
            #pin_clock=GPIO22.SCLK,
        )

        print 'Testing rgb_strip...'
        #test_brightness(rgb_strip)
        #test_rainbow_train(rgb_strip)
        #test_rainbow(rgb_strip)
        test_clock(rgb_strip)
        #test_gravity(rgb_strip)
        #test_many(rgb_strip)

    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        if rgb_strip and rgb_strip.SPI:
            rgb_strip.SPI.close()
        else:
            GPIO.cleanup()
    print 'Bye!'


if __name__ == '__main__':
    main()
