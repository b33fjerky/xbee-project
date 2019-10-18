#! /usr/bin/python

# 802.15.4 Mode
#from xbee.thread import XBee

# All SX module types are digimesh aparently
# DigiMesh Mode
from xbee.thread import DigiMesh
import serial

# This will be ether ttyAMA0 if we're using an IO card or ttyS1 (the ttyUSBx symlink) for the mPCIe card
ser = serial.Serial('/dev/ttyS1', 9600)

# Use an XBee 802.15.4 device
#xbee = XBee(ser,escaped = True) 
# Use an XBee DigiMesh device
xbee = DigiMesh(ser,escaped = True) 

# Specific node 
#REMOTE_NODE_ID = '\x00\x13\xA2\x00\x41\x5D\x15\x18'

# Broadcast to all units
REMOTE_NODE_ID = '\x00\x00\x00\x00\x00\x00\xFF\xFF' 


# Note that it is not required to set DH/DL on remote end as thsi is only used in tranparent comms mode (AP=0) where the devices act as 
# a transparent RS232 connection. 
#
# In API mode this is not needed as all remote frames sent already contain source address that the units will send response to : 
# Page 37  https://store.comet.bg/download-file.php?id=14558#page37

# Remote AT command frame response codes : https://www.digi.com/resources/documentation/Digidocs/90002002/Content/Reference/r_frame_0x97.htm



# Blink LEDs/Toggle all relay outputs (left to right)
xbee.remote_at(   frame_id='1',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P8',
                  parameter='\x05')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='2',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P8',
                  parameter='\x04')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='3',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P7',
                  parameter='\x05')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='4',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P7',
                  parameter='\x04')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='5',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P6',
                  parameter='\x05')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='6',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P6',
                  parameter='\x04')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='7',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P5',
                  parameter='\x05')

print xbee.wait_read_frame()

xbee.remote_at(   frame_id='8',
                  dest_addr_long=REMOTE_NODE_ID,
                  options='\x02',
                  command='P5',
                  parameter='\x04')


print xbee.wait_read_frame()


# BUG : This should report back with a list of decoded values, but it doesn't
# https://github.com/niolabs/python-xbee/issues/69
#
# See decoders for other methods here :
#
# https://github.com/niolabs/python-xbee/blob/master/xbee/backend/ieee.py
# https://github.com/niolabs/python-xbee/blob/master/xbee/backend/zigbee.py

# Voltage temperature inputs expect TMP36 sensor
# https://learn.adafruit.com/tmp36-temperature-sensor/overview
# Temp in degC = [(Vout in mV) - 500] / 10

# 4-20mA sensor inputs give the following range
# 0.4V =  4mA
# 2.0V = 20mA


xbee.remote_at(   frame_id='A',
                  dest_addr_long=REMOTE_NODE_ID,
                  command='IS')

print xbee.wait_read_frame()

# Analogue voltage reference, 0 = 1.25V & 1 = 2.5V (we should have it set to 2.5V)
xbee.remote_at(   frame_id='B',
                  dest_addr_long=REMOTE_NODE_ID,
                  command='AV')


print xbee.wait_read_frame()


# Show XBEE module internal temperature
# The current module temperature in degrees Celsius in 8-bit twos compliment format. 
# For example 0x1A = 26 C, and 0xF6 = -10 C.
#
xbee.remote_at(   frame_id='C',
                  dest_addr_long=REMOTE_NODE_ID,
                  command='TP')

print xbee.wait_read_frame()


# Show XBee responses
#while True:
#    try:
#        response = xbee.wait_read_frame()
#        print response
#    except KeyboardInterrupt:
#        break


ser.close()
