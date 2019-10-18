import sys, time, cmd, serial, binascii, argparse
from utilities import match, bamatch, pamatch, stmatch, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

help_text = '''
### Change Baud Rate ###

Open local serial port (connected to XBEE) using standard serial library,
taking command line arguments for serial port and baud rate settings.

wait 1second
send +++
wait 1second
expect OK response
send ATBD=$newbaud\\r
expect OK response
send ATNB=$newparity\\r
expect OK response
send ATSD=$newstopbits\\r
expect OK response
if --save option used
send ATWR\\r
expect OK response
send ATCN\\r
close serial port
echo "XBEE BAUD setting now Now set to $newbaud,8,$newparity,$newstopbits"
'''

parser = ArgParser(description='Set local XBee Baud Rate', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-port", action='store', dest='port', help="serial port to connect to")
parser.add_argument("-oldbaud", action='store', dest='oldbaud', help="oldbaud, databits, parity, stopbits")
parser.add_argument("-newbaud", action='store', dest='newbaud', help="newbaud, databits, parity, stopbits")
parser.add_argument("--save", action='store_true', dest='save', help="issue a WR to make changes permanent")


# If there are no arguments
if len(sys.argv)==1:
    print "\r\n"
    parser.print_help(sys.stderr)
    sys.exit(1)

else:
	args = parser.parse_args()

	try:
		ser = serial.Serial()
		ser.port 	 = '/dev/' + args.port
		ser.baudrate = args.oldbaud.split(',')[0]
		ser.bytesize = match(args.oldbaud.split(',')[1])
		ser.parity 	 = match(args.oldbaud.split(',')[2])
		ser.stopbits = match(args.oldbaud.split(',')[3])
		
		ser.close()
		ser.open()

		send(ser, '+++')
		receive(ser)

		
		send(ser, 'ATBD={0}\r'.format(bamatch(args.newbaud.split(',')[0])))
		receive(ser)
		
		send(ser, 'ATNB={0}\r'.format(pamatch(args.newbaud.split(',')[2])))
		receive(ser)
		
		send(ser, 'ATSB={0}\r'.format(stmatch(args.newbaud.split(',')[3])))
		receive(ser)


		if args.save:
			send(ser, 'ATWR\r')
			receive(ser)

		send(ser, 'ATCN\r')
		ser.close()

		print 'XBee BAUD setting, now set to {0}'.format(args.newbaud)
		
		
	except serial.SerialException as e:
		print 'Serial Exception:' + e
		sys.exit(1)








