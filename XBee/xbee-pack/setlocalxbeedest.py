import sys, time, cmd, serial, binascii, argparse, os.path
from utilities import match, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

help_text = '''
### Change Destination Address ###

Load in network config dictionary with NI vs addresses.
Translate the remoteaddress NI to DH/DL address using config.
Open local serial port (connected to XBEE) using standard serial library,
taking command line arguments for serial port and baud rate settings.

wait 1second
send +++
wait 1second
expect OK response
send ATDH=$newdh\\r
expect OK response
send ATDL=$newdl\\r
expect OK response
if --save option
send ATWR\\r
expect OK response
echo "XBEE Destination now Set XBEECOM1 (DH=$newdh DL=$newdl)"
send ATCN\\r
close serial port
'''


parser = ArgParser(description='Change Destination Address DH/DL values', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to")
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits")
parser.add_argument("-r", action='store', dest='remote', help="alphanumeric XBEE node name (NI)")
parser.add_argument("--save", action='store_true', dest='save', help="issue a WR to make changes permanent")
parser.add_argument("-d", action='store_true', dest='discovery', help="switch network discovery on/off")

# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

else:
	Dictionary = {}
	args = parser.parse_args()

	if not args.discovery:

		if os.path.exists('network.conf'):
			with open("network.conf", 'r') as f:
				for line in f:
					(node, address) = line.strip().split('|')
					Dictionary.update({node:address})
					print Dictionary
			if args.remote not in Dictionary.keys():
				print "XBee module \"{0}\" not found in network.conf\nExecuting network discovery.".format(args.remote)
				args.discovery = True

		else:
			args.discovery = True

	try:


		ser = serial.Serial(timeout=3)
		ser.port 	 = '/dev/' + args.port
		ser.baudrate = args.baud.split(',')[0]
		ser.bytesize = match(args.baud.split(',')[1])
		ser.parity 	 = match(args.baud.split(',')[2])
		ser.stopbits = match(args.baud.split(',')[3])
		
		ser.close()
		ser.open()
		time.sleep(1)
		send(ser, '+++')
		time.sleep(1)
		receive(ser)

		if args.discovery == True:
			send(ser, 'ATND\r')
			#ser.flush()
			Dictionary2 = receive(ser)
			print Dictionary2
			#time.sleep(5)

			# Repopulate network.conf
			with open('network.conf', 'w') as f:
				f.truncate(0)
				for module, response in Dictionary2.items():
					f.write(module + '|' + response[4:20] + '\n')

			if args.remote in Dictionary2.keys():
				for module, response in Dictionary2.items():
					
					if module == args.remote:
						newDH = response[4:12]
						print newDH
						newDL = response[12:20]
						print newDL
			else:
				print "\nSupplied incorrect remote Node ID.\n"
				exit(1)

		else:
			with open('network.conf', 'r') as f:
				for line in f:
					(nodeid, address) = line.strip().split('|')
					Dictionary.update({node:address})

			for node, address in Dictionary.items():
				if args.remote == node:
					newDH = Dictionary[node][0:8]
					newDL = Dictionary[node][8:16]
				


		send(ser, 'ATDH={0}\r'.format(newDH))
		receive(ser)

		send(ser, 'ATDL={0}\r'.format(newDL))
		receive(ser)

		if args.save:
			send(ser, 'ATWR\r')
			receive(ser)

		send(ser, 'ATCN\r')
		receive(ser)

		ser.close()
		
		print 'XBee Destination now Set {0} (DH={1}  DL={2})'.format(args.remote, newDH, newDL)
		
		
	except serial.SerialException as e:
		print 'Serial Exception:' + e
		sys.exit(1)








