import serial
import time
from xbee import ZigBee

def ProcessData(data):
	print "data arrived"
	f = open('/srv/machines/o.txt','w')
	f.write('hi there\n') # python will convert \n to os.linesep
	f.write(data)
	f.write('\n') # python will convert \n to os.linesep
	f.close()

# Oxygen meter XBee
XbeeId = "0013a20040a82fb3".decode("hex")
# Nitrogen level meter XBee
#XbeeId = "0013a20040a096b1".decode("hex")
# Liquefier level meter
# XbeeId = "0013A20040BF8F59".decode("hex")

serial_port = serial.Serial('/dev/ttyUSB0', 19200, timeout=20)
xbee = ZigBee(serial_port, escaped=False, callback=ProcessData)
while True:
	try:
		print "Here"
		xbee.tx(frame='\x07', dest_addr='\xFF\xFE', dest_addr_long=XbeeId, data='ReadBottlesPressure')
		packet = xbee.wait_read_frame()
		print packet
		time.sleep(3.0)		
	except KeyboardInterrupt:
		break

xbee.halt()
serial_port.close()
