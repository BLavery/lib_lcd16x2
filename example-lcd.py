
# THIS EXAMPLE IS FOR I2C-CONNECTED LCD, NOT 8-BIT OR 4-BIT PARALLEL CONFIGURATION.

# VOLTAGE WARNING. the LCD 16 x 2   is a 5V device.
# With the I2C backplate, the combination is still a 5V device.
# Therefore, without careful 5/3.3 i2c interfacing, or PCB/pin modifications,
# the LCD with I2C addon should not be used on Raspberry Pi.
# RPi / LCD interfacing can be better done with 4-bit GPIO-driven mode, not with I2C addon.

import virtGPIO as GPIO
# import RPi.GPIO as GPIO
# Here is where you would swap to Raspberry Pi mode, IF YOU HAVE USED CORRECT LEVEL SHIFTING ON SCL & SDA.


from lib_lcd16x2 import LCD16x2
import time


# Alas, I2C piggyback boards for 16x2 LCD have various pin connections. What is yours?
# This PCB pin config overrides the default (en 4   rw 5   rs 6   bl -7):

LCD16x2.RSbit = 0
LCD16x2.RWbit = 1
LCD16x2.ENbit = 2
LCD16x2.BLbit = 3

# We need firstly to create an I2C "bus" object, in the SMBus model:
if GPIO.RPI_REVISION > 0:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        from smbus import SMBus
        i2cbus = SMBus(GPIO.RPI_REVISION-1)  # SMBus(0) or SMBus(1) depending board revision
else:
        i2cbus = GPIO.I2C(True)
        #i2cbus.detect()     # optional diagnostic: find devices on I2C bus.  Comment out when finished with this!

# Now create the LCD object, giving it the bus and address:
LCD = LCD16x2(i2cbus, 0x27)  # 0x20-27 is std i2c address of lcd

# OK. Let's print something nonsensical to the display:
LCD.put_char('A')
LCD.put_str(" bcdefghijklmnop") # overflows
LCD.cursor(0,1)   # ie start of second row
LCD.put_str("66")
time.sleep(2)


LCD.put_str("77")
LCD.cursor(1,0)   # ie second on top row
LCD.put_char('.')
LCD.display(blinkON=False)
time.sleep(2)

LCD.display(False)
time.sleep(2)
LCD.backlite(False)
