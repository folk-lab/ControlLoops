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
	print('Transmitted: {0}'.format(cmd.decode()))

def requestAllSensors(xb, delay = 1.0):
    response = qweb.getLoggableInfoForNow('xbee')
    sensors = str.split(response, "\n")
    # print('server wants: ', sensors)
    for sensor_str in sensors:
        if sensor_str !='':
            sensor_dict = {s.split('=')[0]:s.split('=')[1] for s in sensor_str.split(';')}
            if sensor_dict['machine_type']=='xbee':
                try:
                    transmitRequest(xb, sensor_dict['loggable_name'])
                except Exception as e:
                    print('{0} -- {1}'.format(datetime.datetime.now(),e))
                    pass
                time.sleep(delay)

def log_incoming_data(packet):
    """ handle received data packets. log incoming values to server. """
    if packet['id'] == 'rx': # some data was received
        data = packet['rf_data'].decode('utf-8').split('=')
        if data[1]!='':
            print('{0} -- Logged: {1}'.format(datetime.datetime.now(), data))
            qweb.makeLogEntry(*data)
        else:
            print('No data in packet: {0}'.format(packet))	
            pass
	
#### Main Control Loop ####

if __name__ == "__main__":
	
    ser=serial.Serial('/dev/ttyUSB0', 19200) # open serial port
    xb = ZigBee(ser, escaped = True, callback=log_incoming_data) # create zigbee object
            
    while True:
        try:
            requestAllSensors(xb, delay = 5.0)
        except KeyboardInterrupt:
            break

    xb.halt()
    ser.close()
