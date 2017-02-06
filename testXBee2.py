import serial
from xbee import ZigBee
import time
import struct
import pprint

#XbeeId = "0013a20040a13ff8".decode("hex")

# Oxygen meter XBee
#XbeeId = "0013a20040a82fb3".decode("hex")

# Nitrogen level meter XBee
XbeeId = "0013a20040a096b1".decode("hex")

# Liquefier level meter
#XbeeId = "0013A20040BF8F59".decode("hex")

ser = serial.Serial('/dev/ttyUSB0', 19200)
xbee = ZigBee(ser, escaped = True)

attempts = 0
success = 0

#print "Trying to get a packet."
#packet = xbee.wait_read_frame()
#print "Got it", packet['source_addr_long']

while success==0 and attempts<100:
	try:
		xbee.tx(frame='\x07', dest_addr='\xFF\xFE',
                        dest_addr_long=XbeeId, data='ReadC')
		packet = xbee.wait_read_frame()
		if packet['id']=="tx_status": # and packet['frame_id']=='\x07':
			success=1
			print "Packet was sent and received successfully "
			print packet
	except Exception as e:
		print e
	attempts += 1
	time.sleep(1)
try:
	packet = xbee.wait_read_frame()
	print "Got it"
	source = packet['source_addr_long']
	source_addr_long= ''.join(x.encode('hex') for x in source)
	print source_addr_long
	
	XbeeId_long = ''.join(x.encode('hex') for x in XbeeId)
	print XbeeId_long
	
	print packet['id']
	
	if packet['id']=="rx" and source == XbeeId:
		print "Addresses match."
		rf_data = packet['rf_data']
		print "RF Data: ", rf_data
except KeyboardInterrupt:
	print "Keyboard interrupted"

ser.close()
