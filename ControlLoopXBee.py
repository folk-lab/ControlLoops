import serial
from xbee import ZigBee
import time
import datetime
import qweb

# There are 2 XBee emitters in the lab
#     XBee (1) -- by the purifier. reads helium bottle pressure and oxygen level after purifier
#     XBee (2) -- mounted on the liquifier. reads liquefier level.

# There is 1 XBee receiver in the lab.
#     XBee (3) -- mounted on qdot-server 

########## ASYNC TX/RX ###########

def transmitRequest(xb, loggable_name):

	packet = None
	
	# figure out what we are going to read
	if loggable_name=="oxygen_after_purifier":
		XbeeId = b'\x00\x13\xA2\x00\x40\xA8\x2F\xB3' # XBee 1
		cmd = b'ReadOxAftr'
	elif loggable_name=="bottles_pressure":
		XbeeId = b'\x00\x13\xA2\x00\x40\xA8\x2F\xB3' # XBee 1
		cmd = b'ReadBotPrs'
	elif loggable_name=="liquefier_level":
		XbeeId = b'\x00\x13\xa2\x00\x40\xbf\x8f\x59' # XBee 2
		cmd = b'ReadLiq'
	else:
		raise KeyError('Unknown loggable_name: '+loggable_name)
	
	# transmit request for data
	xb.tx(frame=b'\x02', dest_addr=b'\xFF\xFE', dest_addr_long=XbeeId, data=cmd)
	print('Transmitted: {0}'.format(cmd))

def requestAllSensors(xb, delay = 1.0):
	response = qweb.getLoggableInfoForNow('xbee')
	sensors = str.split(response, "\n")
#	print(sensors)
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
			if machine_type == "xbee": # what is the purpose of machine_type?
				try:
					transmitRequest(xb, loggable_name)
					time.sleep(delay)
				except Exception as e:
					print(str(datetime.datetime.now()), ": ",e)

def log_incoming_data(packet):
	""" handle received data packets. log incoming values to server. """
	print(packet)
	if packet['id'] == 'rx': # some data was received
		print('rx received: {0}'.format(packet))
		data = packet['rf_data'].decode('utf-8').split('=')
		print(type(data[1]))
		if data[1]!='':
			print('{0} -- Logged: {1}'.format(datetime.datetime.now(), loggable_name)) 	
			qweb.makeLogEntry(data[0], data[1])
		else:
			print('Empty packet: {0}'.format(packet))	
				
#### Main Control Loop ####

if __name__ == "__main__":
	
	ser=serial.Serial('/dev/ttyUSB0', 19200) # open serial port
	xb = ZigBee(ser, escaped = True, callback=log_incoming_data) # create zigbee object

	while True:
        try:
            requestAllSensors(xb, delay = 5.0)
        except KeyboardInterrupt:
            # print(str(datetime.datetime.now()), ": ", e)
            break

	xb.halt()
    serial_port.close()
