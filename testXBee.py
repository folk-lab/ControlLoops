import serial
from xbee import ZigBee
import time
import struct

'''
mi = [	["liquefier_level", 		"0013a20040a096f7"],
	["oxygen_after_purifier",	"0013a20040a82fb3"],
	["green_dewar_helium_level", 	"0013a20040a096b1"]]


ser = serial.Serial('/dev/ttyUSB0', 9600)
xbee = XBee(ser)

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response
    except KeyboardInterrupt:
        break
        
ser.close()
'''

def ReadXBee(machine_id, waitread):
	#mi = [	["liquefier_level", 		"0013a20040a096f7"],
	#	["oxygen_after_purifier",	"0013a20040a82fb3"],
	#	["green_dewar_helium_level", 	"0013a20040a096b1"]]
	
	ser=serial.Serial('/dev/ttyUSB0', 9600, timeout=20)
	ser.flushInput()
	xbee=ZigBee(ser)

	myRouter=machine_id

	xbee.remote_at(dest_addr_long=myRouter,command='IR',parameter='\x00\x00')
	xbee.remote_at(dest_addr_long=myRouter,command='D4',parameter='\x05')
	time.sleep(waitread)
	xbee.remote_at(dest_addr_long=myRouter,command='IR',parameter='\x00\x00')
	reply=xbee.wait_read_frame(timeout=20)
	
	val = ""
	if reply['source_addr_long'] == machine_id:
		val = str(reply['rf_data'])

	xbee.remote_at(dest_addr_long=myRouter,command='D4',parameter='\x04')
	time.sleep(1)
	ser.flushInput()
	return val

machine_id_string = "0013a20040a096b1"
val = ReadXBee(machine_id_string.decode("hex"), 5)
print val
'''
waitread = 1

machine_id=machine_id_string.decode("hex")

ser=serial.Serial('/dev/ttyUSB0', 19200, timeout=120)
ser.flushInput()
xbee=ZigBee(ser)

myRouter=machine_id

xbee.remote_at(dest_addr_long=myRouter,command='IR',parameter='\x00\x00')
xbee.remote_at(dest_addr_long=myRouter,command='D4',parameter='\x05')
time.sleep(waitread)
xbee.remote_at(dest_addr_long=myRouter,command='IR',parameter='\x00\x00')
reply=xbee.wait_read_frame()

val = ""
if reply['source_addr_long'] == machine_id:
	val = str(reply['rf_data'])

xbee.remote_at(dest_addr_long=myRouter,command='D4',parameter='\x04')
time.sleep(1)
ser.flushInput()
print val
print "Source Address: ", reply['source_addr_long'].encode("hex")
for m in mi:
	if m[1]==reply['source_addr_long']:
		print m[0]
'''
