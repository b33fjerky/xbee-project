#! /usr/bin/python

# All S8 868LPs are DigiMesh type
# XBee = 802.15.4

#from xbee.thread import XBee
from xbee.thread import DigiMesh
import serial

# This will be ether ttyAMA0 if we're using an IO card or ttyS1 (the ttyUSBx symlink) for the mPCIe card
ser = serial.Serial('/dev/ttyS1', 9600)

# use "escaped=True" depending on the API mode in use (Must be SAME on all modules) AP=2

# Use an XBee 802.15.4 device
#xbee = XBee(ser,escaped = True) 

# Use an XBee DigiMesh device
xbee = DigiMesh(ser,escaped = True)


# DH/DL on remote end only used in tranparent comms mode (AP=0) where the devices act as
# a transparent RS232 connection.
#
# In API mode this is not needed as all remote frames sent contain source address

# Configure local XBEE module as the master one, setting the PAN ID to 2513 (same as on all XBEE-IO systems) and the Network Identifier to XBEEPI


xbee.send( 'at',
           frame_id='1', 
           command='AP', 
           parameter='\x02')
print xbee.wait_read_frame()

xbee.send( 'at',
           frame_id='2', 
           command='ID', 
           parameter='\x25\x13')
print xbee.wait_read_frame()

xbee.send( 'at', 
           frame_id='3',
           command='NI', 
           parameter='XBEEPI')
print xbee.wait_read_frame()

xbee.send( 'at', 
           frame_id='4', 
           command='WR')
print xbee.wait_read_frame()

xbee.send( 'at', 
           frame_id='5', 
           command='SH')
print xbee.wait_read_frame()

# BUG : First parameter byte is not shown correctly
xbee.send( 'at', 
           frame_id='6', 
           command='SL')
print xbee.wait_read_frame()



# Remote AT command frame response codes : https://www.digi.com/resources/documentation/Digidocs/90002002/Content/Reference/r_frame_0x97.htm

REMOTE_NODE_ID='\x00\x13\xA2\x00\x41\x5D\x15\x18'
BROADCAST_ID='\x00\x00\x00\x00\x00\x00\xFF\xFF'


# Read back all remote DH/DL Pair settings
xbee.remote_at(   frame_id='8',
                  dest_addr_long=BROADCAST_ID,
                  command='DH')
print xbee.wait_read_frame()

# BUG : First parameter byte is not shown correctly
xbee.remote_at(   frame_id='9',
                  dest_addr_long=BROADCAST_ID,
                  command='DL')

print xbee.wait_read_frame()



# Next we'll use a broadcast AG command to get ALL remote stations to discover/build mesh network paths back to this local node
# and set thier (the remote nodes) DH/DL addresses to match the local node if they have DH+DL address matching the param value
# 
# To skip the DH/DL setting use a dummy address like 'x00\x00\x00\x00\x00\x00\xFF\xFE'
#
# See Page 43  : https://store.comet.bg/download-file.php?id=14558#page43

xbee.send( 'at',
            frame_id='7',
            command='AG',
            parameter='\x00\x00\x00\x00\x00\x00\xFF\xFF')

print xbee.wait_read_frame()


# Read back all remote DH/DL Pairs again (showing if they have changed)
xbee.remote_at(   frame_id='8',
                  dest_addr_long=BROADCAST_ID,
                  command='DH')
print xbee.wait_read_frame()

xbee.remote_at(   frame_id='9',
                  dest_addr_long=BROADCAST_ID,
                  command='DL')

print xbee.wait_read_frame()


# We can resolve a Network Identifier (NI) to a 64 bit address
# Possible BUG : reports back back a wierd looking status param, note the parm field is prefixed with the 16bit reseverved field.
xbee.send( 'at',
           frame_id='A',
           command='DN',
           parameter='XBEEIO')

print xbee.wait_read_frame()


# We can resolve a 64Bit address back to it's Network Identifier (NI)
xbee.remote_at(   frame_id='B',
                  dest_addr_long=REMOTE_NODE_ID,
                  command='NI')


print xbee.wait_read_frame()

ser.close()
