import sys, time, cmd, serial, binascii, argparse, os.path, re
from xbee.thread import DigiMesh
from utilities import bamatch, pamatch, stmatch


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)




help_text = '''
\r\n### Set remote XBee DH/DL ###

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
parser.add_argument("-ad", action='store', dest='address',help="user supplied address for AG command" )
parser.add_argument("--save", action='store_true', dest='save', help="issue WR command to persist changes" )

# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
else:
	## Start up ##
	args = parser.parse_args()
	ser   = serial.Serial('/dev/' + args.port, args.baud.split(',')[0])
	XBee  = DigiMesh(ser)
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
	print "\n\nGet SH/SL from main XBee HUB:\n"
	XBee.send(
				'at',
				frame_id='1',
				command='SH'
			 )
	print "\tATSH"
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		SH = response['parameter'].encode("hex")
		print "\tOK (SH={0})\n".format(SH)

	XBee.send(
				'at',
				frame_id='2',
				command='SL'
			 )
	print "\tATSL"
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		SL = response['parameter'].encode("hex")
		print "\tOK (SL={0})\n".format(SL)




	print "\n\nSet remote DH/DL to main HUB SH/SL:\n"
	XBee.send(	'remote_at',
				dest_addr_long=binascii.unhexlify(DevList[args.remote]),
				frame_id='3',
				command='DH',
				parameter=binascii.unhexlify(SH)
			 )
	print "\tATDH"
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	XBee.send(	'remote_at',
				dest_addr_long=binascii.unhexlify(DevList[args.remote]),
				frame_id='4',
				command='DL',
				parameter=binascii.unhexlify(SL)
			 )
	print "\tATDL"
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	XBee.send(	'remote_at',
				dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',
				frame_id='5',
				command='AG',
				parameter=args.address
			 )
	print "\tATAG={0}".format(args.address)
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)


	if args.save:
		## Persist changes ##
		XBee.send(	'remote_at',
					dest_addr_long=binascii.unhexlify(DevList[args.remote]),
					frame_id='6',
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
				frame_id='7',
				command='AC' 
			 )
	print "\tATAC"
	response = XBee.wait_read_frame()
	if response['status'].encode("hex") == '00':
		print "\tOK\n"

	time.sleep(0.5)

	print "\nRemote module {0}, successfully set DH to {1}".format(args.remote, SH)
	print "Remote module {0}, successfully set DL to {1}".format(args.remote, SL)
	print "\n"








