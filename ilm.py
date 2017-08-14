import serial
import time

EOL = '\r'	# End of line character for the ILM


class ILM:
	# Constructor. This is called when an object of type IGH is created.
	# Example obj = IGH('/dev/ttyS1', 9600, 5)
	# This example will create an instance of the IGH class called obj which can be used to talk to IGNHN (isobus#5)
	# Owner is the process that made the object. It should be a name unique to a process that is used to lock the serial port.
	def __init__(self, port_name, baudrate, machine_id):
		self.serial_port = serial.Serial(port_name, baudrate=baudrate, timeout=1, stopbits=2)
		self.machine_id = machine_id # this is the ISOBUS address
	
	def __del__(self):
		self.serial_port.close()
	
	# ATTENTION:	Don't use this when several ISOBUS devices are connected and powered on
	# ALSO: 		Don't forget to save the changes into the permanent memory after running this function
# 	def setIsobusAddress(self, address):
# 		response = ''
# 		to_write = 'U1!{:d}{}'.format(address, EOL)
# 		wrote = self.serial_port.write(to_write.encode('latin1'))
# 		ch = ''
# 		t = time.time()			# Don't try to read forever, if there's nothing
# 		while ch != EOL and time.time() - t < 1:
# 			ch = self.serial_port.read().decode('utf-8')
# 			response += ch
# 		self.serial_port.flush()
# 
# 		to_write = 'U0{}'.format(EOL)
# 		wrote = self.serial_port.write(to_write.encode('latin1'))
# 		ch = ''
# 		t = time.time()			# Don't try to read forever, if there's nothing
# 		while ch != EOL and time.time() - t < 1:
# 			ch = self.serial_port.read().decode('utf-8')
# 			response += ch
# 		self.serial_port.flush()		
# 		
# 		self.machine_id = address
# 		return response
		
	def runCommand(self, cmd):
		response = ''

		to_write = '@{:d}{}{}'.format(self.machine_id, cmd, EOL)
		if not self.serial_port.isOpen():
			self.serial_port.open()

		self.dirty = 1
		
		wrote = self.serial_port.write(to_write.encode('latin1'))
		if wrote != len(to_write):
			print('COMMAND FAILED: ', cmd)
		

		t = time.time()			# Don't try to read forever, if there's nothing
		ch = ''
		while ch != EOL and time.time() - t < 1:
			ch = self.serial_port.read().decode('utf-8')
			response += ch
	
		self.serial_port.flush()
		if cmd[:1] == 'N':
			print('To Write: ', to_write)
		if response[:1] == '?':
			print('Error: ', response)
		return response
	
	# This will return the helium level if the current isobus machine_id corresponds to an ILM
	def getHeliumLevel(self):
		output = self.runCommand('R1')
		self.HeliumLevel = float(output[3:])/10
		return self.HeliumLevel

	# This will return the nitrogen level if the current isobus machine_id corresponds to an ILM		
	def getNitrogenLevel(self):
		output = self.runCommand('R2')
		self.NitrogenLevel = float(output[3:])/10
		return self.NitrogenLevel
	
	def setRemote(self):
		self.runCommand('C3')

	def setLocal(self):
		self.runCommand('C2')
	

