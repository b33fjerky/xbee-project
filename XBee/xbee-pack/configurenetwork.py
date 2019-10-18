import sys, time, cmd, serial, binascii, argparse, os.path, re
from xbee.thread import DigiMesh, XBee
from utilities import netdiscovery
#from digi.xbee.models.address import XBee64BitAddress, XBee16BitAddress
#from digi.xbee.devices import DigiMeshDevice, RemoteDigiMeshDevice
#from digi.xbee.packets.common import RemoteATCommandPacket
#from utilities import match, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)




help_text = '''
\r\n### Build network routes - AG Command ###

Example:
	
	Use default address FFFF:
	./configurenetwork.py -p ttyUSB1 -b="9600,8,N,1" 

	Use user supplied address:
	./configurenetwork.py -p ttyUSB1 -b="9600,8,N,1" -a FF11

\r\n
'''


parser = ArgParser(description='Change Destination Address DH/DL values', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to", required=True)
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits", required=True)
parser.add_argument("-a", action='store', dest='address', help="user supplied address for AG command")

# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
else:
	
	args = parser.parse_args()

	DevList = {}

	if not args.address:
		args.address = 'FFFF'


	regex = re.compile("status\': \'..(00)\'")
	ser = serial.Serial('/dev/' + args.port, args.baud.split(',')[0])
	XBee = DigiMesh(ser)

	DevList = netdiscovery(XBee)


	print "\n\nEntered (Command Mode) on local main XBee HUB:\n"
	## Set local XBee PAN ID to 2513 	##
	XBee.send( 	'at',
				frame_id='1',
				command='ID',
				parameter=binascii.unhexlify('2513')
			 )
	print "\tATID=2513"  
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	## Set Local XBee Node ID to XBEEPI ##
	XBee.send(	'at',
				frame_id='2',
				command='NI',
				parameter='XBEEPI' 
			 )
	print "\tATNI=XBEEPI"  
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	## Apply changes to local XBee 		##
	XBee.send(	'at',
				frame_id='3',
				command='AC' 
			 )
	print "\tATAC"  
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK"

	time.sleep(0.5)


	print "\n\nAG command on broadcast address:\n"
	## AG Command
	## 		- Builds mesh routes 
	## 		- Configures remote DH/DL
	XBee.send(	'remote_at',
				dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',
				frame_id='4',
				command='AG',
				parameter=args.address
			 )
	## For each remote module discovered (network.conf) line 59 ##
	print "\tATAG={0}".format(args.address) 
	for node, address in DevList.items():
		tmp = re.search( regex, str(XBee.wait_read_frame()))
		if tmp.group(1) == '00':
			print "\tOK - {0}".format(node)
		else:
			"\tFail - {0}".format(node)
			exit(1)

	time.sleep(0.5)


	print "\n\nPersist changes on remote COM modules:\n"
	
	## WR - persist changes for each COM module ##
	for node, address in DevList.items():
		if 'COM' in node:
			XBee.send( 	'remote_at',
						dest_addr_long=binascii.unhexlify(address),
						frame_id='5',
						command='WR'
					 )
			print "\tATWR" 
			tmp = re.search( regex, str(XBee.wait_read_frame()))
			if tmp.group(1) == '00':
				print "\tOK"
			else:
				"\tFail"
				exit(1)

			print "\n"
			time.sleep(0.5)	




