#!/usr/bin/python
# -*- coding: utf8 -*-
from collections import namedtuple
import time

import RPi.GPIO as GPIO

from button import Button
from lcd import LCD

"""
TODO:
    Make button press on STATE.GOING work properly
"""


class STATE():
    GO = 0
    STOPPING = 1
    STOPPED = 2
    GOING = 3


"""
state -> StateInfo(
    NAME='<name>',
    DELAY=<seconds>,
    OUTPUT=(red, amber, green),
    NEXT_STATE=STATE.<next_state>,
}
"""
StateInfo = namedtuple('StateInfo', ['NAME', 'DELAY', 'OUTPUT', 'NEXT_STATE'])
STATE_INFO = {
    STATE.GO: StateInfo(
        NAME='Go',
        DELAY=20.0,
        OUTPUT=(False, False, True),
        NEXT_STATE=STATE.STOPPING,
    ),
    STATE.STOPPING: StateInfo(
        NAME='Stopping',
        DELAY=2.5,
        OUTPUT=(False, True, False),
        NEXT_STATE=STATE.STOPPED,
    ),
    STATE.STOPPED: StateInfo(
        NAME='Stopped',
        DELAY=5.0,
        OUTPUT=(True, False, False),
        NEXT_STATE=STATE.GOING,
    ),
    STATE.GOING: StateInfo(
        NAME='Get ready',
        DELAY=2.5,
        OUTPUT=(True, True, False),
        NEXT_STATE=STATE.GO,
    ),
}


class Traffic(object):
    """
    Emulates a set of traffic lights
    """

    def __init__(
            self,
            pin_red=14,
            pin_amber=3,
            pin_green=2,
            lcd=None,
            lcd_line=None,
        ):
        self.LED_RED = pin_red
        self.LED_AMBER = pin_amber
        self.LED_GREEN = pin_green
        self.LCD = lcd
        self.LCD_LINE = lcd_line

        self.STATE = STATE.GOING
        self.WAITING = False

        self.NEXT_CHANGE = 0

        self._init_pins()

    def _init_pins(self):
        # Setup all the pins as outputs
        GPIO.setup(self.LED_RED, GPIO.OUT)
        GPIO.setup(self.LED_AMBER, GPIO.OUT)
        GPIO.setup(self.LED_GREEN, GPIO.OUT)

        # Start
        GPIO.output(self.LED_RED, False)
        GPIO.output(self.LED_AMBER, False)
        GPIO.output(self.LED_GREEN, False)

    def push_the_button(self):
        if self.STATE != STATE.STOPPED:
            self.WAITING = True
            if self.STATE == STATE.GO:
                # Make sure we are changing soon
                self.NEXT_CHANGE = min(
                    self.NEXT_CHANGE,
                    time.time() + 2.0
                )

    @property
    def is_waiting(self):
        return self.WAITING

    REMAINING_TIME_PREV = None
    def update(self):
        # Should we move to a new state?
        if time.time() >= self.NEXT_CHANGE:
            # Change current state
            self.STATE = STATE_INFO[self.STATE].NEXT_STATE

            if self.STATE == STATE.STOPPED:
                self.WAITING = False

            # Show the new state
            self._show_state()

            # Work out when we should next change state
            self.NEXT_CHANGE = time.time() + STATE_INFO[self.STATE].DELAY

        remaining_time = int((self.NEXT_CHANGE - time.time()) * 10) / 10.0
        if remaining_time != self.REMAINING_TIME_PREV:
            self.LCD.output_line(
                '{state} for {remaining_time}s...'.format(
                    state=STATE_INFO[self.STATE].NAME,
                    remaining_time=remaining_time,
                ),
                self.LCD_LINE,
            )

    def _show_state(self):
        # Update the shown state
        outputs = STATE_INFO[self.STATE].OUTPUT
        GPIO.output(self.LED_RED, outputs[0])
        GPIO.output(self.LED_AMBER, outputs[1])
        GPIO.output(self.LED_GREEN, outputs[2])


def main():
    print 'Hello!'
    try:
        print 'Initialising...'
        GPIO.setmode(GPIO.BCM)
        lcd = LCD(
            pin_rs=4,
            pin_e=25,
            pins_d=[24,23,22,27],
        )
        traffic = Traffic(
            pin_red=14,
            pin_amber=3,
            pin_green=2,
            lcd=lcd,
            lcd_line=0,
        )
        button = Button(
            pin=11,
        )
        GPIO.setup(8, GPIO.OUT)

        print 'Testing traffic lights...'
        while True:
            if button.was_pushed():
                traffic.push_the_button()
            GPIO.output(
                8,
                traffic.is_waiting,
            )
            traffic.update()
            time.sleep(0.1)



    except KeyboardInterrupt:
        pass
    finally:
        print 'Cleaning up...'
        GPIO.cleanup()
    print 'Bye!'


if __name__ == '__main__':
    main()
