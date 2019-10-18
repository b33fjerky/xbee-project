import sys, time, cmd, serial, binascii, argparse, os.path, re
from xbee.thread import DigiMesh
from utilities import bamatch, pamatch, stmatch, netdiscovery


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)




help_text = '''
\r\n### Set remote XBee Baud Rate ###

Examples:
	
	Agonly:
	 

	remote address and save:
	

\r\n
'''


parser = ArgParser(description='Change Destination Address DH/DL values', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to", required=True)
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits", required=True)
parser.add_argument("-ag", action='store_true', dest='agonly', help="skip section setting DH/DL directly and only execute AG section")
parser.add_argument("-r", action='store', dest='remote', help="remote module node ID", required=True)
parser.add_argument("-rb", action='store', dest='remotebaud', help="remote module target baud rate", required=True)
parser.add_argument("-ad", action='store', dest='address',help="user supplied address for AG command" )
parser.add_argument("--save", action='store_true', dest='save', help="issue WR command to persist changes" )

# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
else:
	## Start up ##
	args = parser.parse_args()
	ser = serial.Serial('/dev/' + args.port, args.baud.split(',')[0])
	XBee = DigiMesh(ser)
	DevList = {}
	## Start up ##



	## network.conf ##
	if not args.address:
		args.address = 'FFFE'

	if os.path.exists('network.conf'):
		with open("network.conf", 'r') as f:
			for line in f:
				(node, address) = line.strip().split('|')
				DevList.update({node:address})
	else:
		print("File network.conf does not exist, or is not in path.\n")
		print("Try scanning the network?")
		print("(Y/n)")
		answer = raw_input()
		if answer == 'Y' or answer == 'y':
			DevList = netdiscovery(XBee)
			print "\n"
		else: 
			print "Exiting."
			exit(1)


	if args.remote in DevList.keys():
		pass
	elif args.remote not in DevList.keys():
		print("\nError: Remote XBee Node ID not found in network.conf (DevList).\n Try scanning the network ?\n")
		print("(Y/n)")
		answer = raw_input()
		if answer == 'Y' or answer == 'y':
			DevList = netdiscovery(XBee)
		else: 
			print "Exiting."
			exit(1)
	## network.conf ##



	## Commands
	print "\n\nEntered (Command Mode) on remote module {0}:\n".format(args.remote)
	## Set remote Baud Rate ##		
	XBee.send( 	'remote_at',
				dest_addr_long=binascii.unhexlify(DevList[args.remote]),
				frame_id='1',
				command='BD',
				parameter=binascii.unhexlify('0' + bamatch(args.remotebaud.split(',')[0])) 
			 )## 9600 baud is pamatch -> 3 | binascii.unhexlify('03') = \x03 <- format requested by niolabs	
	
	print "\tATBD=" + args.remotebaud.split(',')[0] 
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	## Set remote Parity    ##
	XBee.send(	'remote_at',
				dest_addr_long=binascii.unhexlify(DevList[args.remote]),
				frame_id='2',
				command='NB',
				parameter=binascii.unhexlify('0' + pamatch(args.remotebaud.split(',')[2]))
			 )

	print "\tATNB=" + args.remotebaud.split(',')[2] 
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	## Set remote Stop Bits ##
	XBee.send(	'remote_at',
				dest_addr_long=binascii.unhexlify(DevList[args.remote]),
				frame_id='3',
				command='SB',
				parameter=binascii.unhexlify('0' + stmatch(args.remotebaud.split(',')[3]))
			 )

	print "\tATSB=" + args.remotebaud.split(',')[3] 
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	if args.save:
		## Persist changes ##
		XBee.send(	'remote_at',
					dest_addr_long=binascii.unhexlify(DevList[args.remote]),
					frame_id='4',
					command='WR'
				 )
		print "\tATWR"
		response = XBee.wait_read_frame()
		if response['status'].encode("hex") == '00':
			print "\tOK\n"

		time.sleep(0.5)


	## Apply changes ##
	XBee.send(	'remote_at',
				dest_addr_long=binascii.unhexlify(DevList[args.remote]),
				frame_id='5',
				command='AC' 
			 )
	print "\tATAC"
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)

	print "\n"







