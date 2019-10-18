
import serial
import time
from digi.xbee.util import utils
from digi.xbee.io import IOLine, IOValue
from digi.xbee.models.address import XBee64BitAddress
from digi.xbee.devices import XBeeDevice, DigiMeshDevice, RemoteDigiMeshDevice, RemoteXBeeDevice

def NetworkDiscovery(MainHub):
    # Network Discovery 
    NodeID   = []
    Address  = []
    XBeeNetwork = MainHub.get_network()
    XBeeNetwork.clear()
    XBeeNetwork.set_discovery_timeout(4)
    XBeeNetwork.start_discovery_process()


    

    while XBeeNetwork.is_discovery_running():       
        time.sleep(0.2)


    Devices = XBeeNetwork.get_devices()
    for dev in Devices:
        NodeID.append(dev.get_node_id())
        Address.append(str(dev.get_64bit_addr()))
        
    DevList = dict(zip(NodeID, Address))

    return DevList


PORT = "/dev/ttyS1" 
BAUD_RATE = 9600
RPi = XBeeDevice(PORT, BAUD_RATE)

RPi.open()
#DevList = NetworkDiscovery(RPi)
#print (DevList)


#RPi.set_parameter("AP", 2)

RemoteXBee = RemoteXBeeDevice(RPi, XBee64BitAddress.from_hex_string('0013A2004187A831'))
#RPi.send_data(RemoteXBee,"AT")
print(RemoteXBee.get_parameter("NI"))
print(RPi.get_parameter("AP"))
RPi.set_parameter("DH", utils.hex_string_to_bytes("0013A200"))
#RPi.set_parameter("DL", utils.hex_string_to_bytes("4187A831"))
#RPi.get_parameter("AG")
#RemoteXBee.set_parameter("SH", utils.hex_string_to_bytes("00000000"))
print("Local XBee Destination address high:    %s" % utils.hex_to_string(RPi.get_parameter('DH')))
print("Local XBee Destination address low:     %s" % utils.hex_to_string(RPi.get_parameter('DL')))

#print("Remote XBee Source address high:    %s" % utils.hex_to_string(RemoteXBee.get_parameter('SH')))
#print("Remote XBee Source address low:     %s" % utils.hex_to_string(RemoteXBee.get_parameter('SL')))

#print(bytearray(1))
#print()
#RPi.send_data(RemoteXBee, "AT")
#print(RPi.read_data())
#print(RPi.get_parameter("AP"))
#enter_at_command_mode(RPi)
#RPi.set_parameter("NI", bytearray("XBEEPI","utf8"))
#RPi.set_parameter("AP", bytearray("\x00","utf8"))
print(RPi.get_parameter("AP"))

#print(RemoteXBee.get_parameter("NI"))


if RPi is not None and RPi.is_open():
    print("\n")
    RPi.close()





