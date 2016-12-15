""" a driver to control the on/off functions of the magnet heater """

import serial

class Heater():
    """ a class for controling the Lakeshore 370 resistance bridge """

    def __init__(self, com):
        """ open port and set default state """
    
        try:
            self.ctrl = serial.Serial(com, 9600, timeout=1)
        except:
            raise IOError("Could not connect to serial port: {0}".format(com))
        self.ctrl.setDTR(True) # make sure the heater is off when this script is started
                               # should be true as soon as the port is initialized
                               # this is redundant
            
    def close(self):
        """ closes the VISA instance """
        self.ctrl.close()
        
    def relay_on(self):
        """ turns the relay on """
        self.ctrl.setDTR(False)
        
    def relay_off(self):
        """ turns the relay on """
        self.ctrl.setDTR(True)