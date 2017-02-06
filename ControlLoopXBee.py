import serial
from xbee import ZigBee
import time
import datetime
import struct
import qweb
import binascii

ser=serial.Serial('/dev/ttyUSB0', 19200)
xbee = ZigBee(ser, escaped = True)

def ReadXBee(loggable_name):
	#print loggable_name
	packet = None
	if loggable_name=="oxygen_after_purifier":
		XbeeId = b'\x00\x13\xA2\x00\x40\xA8\x2F\xB3'
		cmd = b'ReadOxAftr'
	elif loggable_name=="bottles_pressure":
		XbeeId = b'\x00\x13\xA2\x00\x40\xA8\x2F\xB3'
		cmd = b'ReadBotPrs'
	elif loggable_name=="liquefier_level":
		XbeeId = b'\x00\x13\xa2\x00\x40\xbf\x8f\x59'
		cmd = b'ReadLiq'
	elif loggable_name=="purifier_nitrogen_level":
		XbeeId = b'\x00\x13\xa2\x00\x40\xa0\x96\xb1'
		cmd = b'ReadC'
	else:
		raise Exception('I don\'t know what to do with this loggable_name.'+loggable_name)
	
	xbee.tx(frame=b'\x02', dest_addr=b'\xFF\xFE', dest_addr_long=XbeeId, data=cmd)
	packet = xbee.wait_read_frame()
	while not packet['id']=="rx":
		packet = xbee.wait_read_frame()
	
	d = packet['rf_data'].decode('utf-8')
	if d.find("=") > -1:
		rf_loggable_name = d.split('=')[0]
		rf_val = d.split('=')[1]
		if not (rf_loggable_name=="purifier_nitrogen_level" and float(rf_val)<71000):
			qweb.makeLogEntry(rf_loggable_name, rf_val)
	else:
		print(packet)

def log():
	response = qweb.getLoggableInfoForNow('xbee')
	sensors = str.split(response, "\n")
	machine_type=""
	for sensor in sensors:
		if sensor != "":
			props = str.split(sensor, ";")
			for prop in props:
				keyvals = str.split(prop, "=")
				if keyvals[0]=="loggable_name":
					loggable_name = keyvals[1]
				elif keyvals[0]=="machine_type":
					machine_type = keyvals[1]
			if machine_type == "xbee":
				try:
					ReadXBee(loggable_name)
				except Exception as e:
					print(str(datetime.datetime.now()), ": ",e)


period_all = 15 #seconds
t_all = 0

while True:
	try:
		if time.time() - t_all >= period_all:
			log()
			t_all = time.time()

		time.sleep(1)
	except Exception as e:
		print(str(datetime.datetime.now()), ": ", e)

xbee.halt()
ser.close()


