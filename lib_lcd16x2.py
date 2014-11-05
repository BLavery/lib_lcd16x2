#!/usr/bin/python
# -*- coding: utf-8 -*-

# THIS LIBRARY IS FOR I2C-CONNECTED LCD, NOT 8-BIT OR 4-BIT PARALLEL CONFIGURATION.

# hd44780.pdf refs are on internet.
# SMBus syntax

# VOLTAGE WARNING. the LCD 16 x 2   is a 5V device.
# With the I2C backplate, the combination is still a 5V device.
# Therefore, without careful 5/3.3 i2c interfacing, or PCB/pin modifications,
# the LCD with I2C addon should not be used on Raspberry Pi.
# RPi / LCD interfacing can be better done with 4-bit GPIO-driven mode, not with I2C addon.


# Alas, I2C piggyback boards for 1602 LCD have various pin connections between 8-pin PCF8574 and LCD part. What is yours?

# http://www.ebay.com.au/itm/1-IIC-I2C-TWI-SPI-Serial-Interface-Board-Module-Port-1602LCD-Display-for-Arduino-/271525182721
# Board with big blue contrast Pot, + sideplug for alternate backlite power.
# Schematic here: www.nimseugjs.com/IC/All%20data%20modules/2284.zip, except 10k pullups on 3 A0-2 pads
# p0=RS   p1=RW   p2=EN   p3=Backlite

# http://www.ebay.com.au/itm/New-5V-IIC-I2C-Serial-Interface-Board-Module-For-Arduino-1602-LCD-Display-/350847514113
# Board with very tiny silver-coloured contrast Pot.  Backlite bit HIGH = off.
# p4=EN   p5=RW   p6=RS   p7=Backlite

# IN ANY CASE LIBRARY BELOW CAN BE CONFIGURED FOR ANY PATTERN OF DATA AND CONTROL PIN CONNECTION.  See example code.

import sys

if __name__ == '__main__':
    print (sys.argv[0], 'is an importable module:')
    print ("...  from", sys.argv[0], "import lib_lcd16x2")
    exit()




import time
#import sys


def _BV(x):
    return 1 << x


# P7 - P0 on the PCF8574 chip:  DEFAULT on my model:
# P7=lite* (Low = lite on) P6=rs(dc*)  P5=rw*  P4=en  P3=db7 P2=db6 P1=db5 P0=db4
_EN = 0x10   # data strobe pin
_READ = 0x20   # We don't use the read
_DATA = 0x40   # DATA vs CMD
_LITEOFF = 0x80
_LITEON = 0

class LCD16x2:

    RSbit = 6
    ENbit = 4
    RWbit = 5
    BLbit = -7    # a MINUS pin number means inverse operation: HIGH = backlight OFF
    DBoffset = 0
    bus = None

    def __init__(self, bus, port):
        # NOTE: bus needs to be defined elsewhere and passed to here.
        # Normally there is only one instance of I2C() bus, and it might have several devices attached!
        global _EN, _READ, _DATA, _LITEOFF, _LITEON
        self.bus = bus
        self.port = port
        #print bus, port
        #print "bits", self.RSbit, self.ENbit, self.RWbit, self.BLbit
        # correct the control bits on PCF8574, depending on how PCB is wired
        _EN = _BV(self.ENbit)
        _READ = _BV(self.RWbit)
        _DATA = _BV(self.RSbit)
        if self.BLbit <0:    # bad luck if board wired backlite to pin p0!
            _LITEOFF = _BV(-(self.BLbit))
            _LITEON = 0
        else:
            _LITEON = _BV(self.BLbit)
            _LITEOFF = 0
        self.lite = _LITEOFF
        #print "masks", _EN, _READ, _DATA, _LITEON


        if (_EN | _DATA) < 0x10:   # found some control bits in low pin numbers
            self.DBoffset = 4   #  p4 - p7
        else:
            self.DBoffset = 0   #  p0 - p3
        #print "dboffset", self.DBoffset, hex(_EN | _DATA)

        # INIT Commands from PCF8574 reference:
        self._write_cmd(0x33, 5)
        self._write_cmd(0x32, 5)
        self._write_cmd(0x28, 5)   # 4 bit 2 line
        self._write_cmd(0x08)   # Display off
        self._write_cmd(0x01, 5)   # cls
        self._write_cmd(0x06)    # ??
        self._write_cmd(0x02, 5)  # cursor home
        self._write_cmd(0x0F)   # Display on, blinking cursor
        self.lite = _LITEON
        self._write_cmd(0x80)    # Row 1 Col 1


    def put_char(self, char):
        global _EN, _DATA
        #print "char", char,
        char = ord(char)
        nibhi = (char>>4)<<self.DBoffset
        #print "hi4", hex(nibhi),
        niblo = (char & 0x0f)<<self.DBoffset
        #print "lo4", hex(niblo),
        # Now CHAR goes out in 2x 4-bit nibbles
        # For each CHAR, we need to strobe the _EN pin on & then off.
        # That makes 4 writes to the PCF8574 chip.
        # Not forgetting the backlite pin & the RS (data/cmd) pin.
        self.bus.write_byte(self.port, nibhi | _DATA | self.lite | _EN)
        time.sleep(0.001)
        self.bus.write_byte(self.port, nibhi | _DATA | self.lite)
        #print hex(nibhi | _DATA | self.lite | _EN),   # diagnostic only
        #print hex(nibhi | _DATA | self.lite ),
        time.sleep(0.001)
        self.bus.write_byte(self.port, niblo | _DATA | self.lite | _EN)
        time.sleep(0.001)
        self.bus.write_byte(self.port, niblo | _DATA | self.lite)
        #print hex(niblo | _DATA | self.lite | _EN),
        #print hex(niblo | _DATA | self.lite)
        time.sleep(0.001)


    def cls(self):
        self._write_cmd(0x01, 5)

    def put_str(self, str):
        for k in range(len(str)):
            self.put_char(str[k])

    def _write_cmd(self, cmd, msec = 0):
        global _EN
        #print "cmd", hex(cmd),
        nibhi = (cmd>>4)<<self.DBoffset
        niblo = (cmd & 0x0f)<<self.DBoffset
        self.bus.write_byte(self.port, nibhi | self.lite | _EN)
        #print hex( nibhi | self.lite | _EN),
        time.sleep(0.001)
        self.bus.write_byte(self.port, nibhi | self.lite)
        #print hex(nibhi | self.lite),
        time.sleep(0.001)
        self.bus.write_byte(self.port, niblo | self.lite | _EN)
        #print hex(niblo | self.lite | _EN),
        time.sleep(0.001)
        self.bus.write_byte(self.port, niblo | self.lite)
        #print hex(niblo | self.lite)
        time.sleep(0.001)
        if msec>0:   # extra delay?
            time.sleep(msec/1000.0)
            #print "sleep", msec/1000.0


    def backlite(self, turnon):
        global _LITEON, _LITEOFF
        self.lite = _LITEON if turnon else _LITEOFF
        self._write_cmd(0x06)   # a harmless CMD output, just to send out the backlite setting.

    def cursor(self, x=0, y=0):
        self._write_cmd(0x80 + (x&0x0f) + ((y&1)*0x40))


    def display(self, displayON=True, cursorON=True, blinkON = True):
        self._write_cmd(0x08 + (4 if displayON else 0) + (2 if cursorON else 0) + (1 if blinkON else 0))


########################################################################
