import visa
import numpy as np
import json
import time, os

frequencies = np.array([9.8, 13.7, 16.2])
units = ['Kelvin', 'Ohms', 'linear data', 'minimum data', 'maximum data']
mode = ['Voltage', 'Current']
voltages = np.array([2e-6, 6.32e-6, 20e-6, 63.2e-6, 200e-6, 632e-6, 
                     2e-3,6.32e-3,20e-3, 63.2e-3, 200e-3, 632e-3])
currents = np.array([1e-12, 3.16e-12, 10e-12, 31.6e-12, 100e-12, 316e-12, 
                     1e-9, 3.16e-9, 10e-9, 31.6e-9, 100e-9, 316e-9, 
                     1e-6, 3.16e-6, 10e-6, 31.6e-6, 100e-6, 316e-6,
                     1e-3, 3.16e-3, 10e-3, 31.6e-3])
resistances = np.array([2.00e-3, 6.32e-3, 20e-3, 63.2e-3, 200e-3, 632e-3, 
                        2.00, 6.32, 20, 63.2, 200, 632, 
                        2.00e3, 6.32e3, 20e3, 63.2e3, 200e3, 632e3,
                        2.00e6, 6.32e6, 20e6, 63.2e6])

                        

class LS370():
    """ a class for controling the Lakeshore 370 resistance bridge """
    def __init__( self, address, interface='GPIB', board = 0):
        rm = visa.ResourceManager()
        if interface == 'GPIB':
            self.ctrl = rm.open_resource('GPIB{0:d}::{1:d}::INSTR'.format(board,address))
            try:
                self_test = self.ctrl.query('*TST?')
            except Exception as e:
                raise EnvironmentError('LakeShore communication failed with error: {}'.format(e))
            if self_test == '1':
                raise EnvironmentError('LakeShore self test at power up reported at least one error.')
            
        if interface == 'Serial':
            from visa import constants
            self.ctrl = rm.open_resource('ASRL{0:d}::INSTR'.format(address), 
                                         data_bits=7, parity=constants.Parity.odd)
            # add some sort of test here
            
    def close(self):
        """ closes the VISA instance """
        self.ctrl.close()
        
    def write( self, command_string ):
        """ send the supplied string to the instrument """
        self.ctrl.write( command_string )
        
    def read( self ):
        """ read raw data from device. there are some other choices here
            but if ask fails, this is probably what you want. """
        return self.ctrl.read_raw()
        
    def query( self, command_string ):
        """ send the supplied string to the instrument """
        return self.ctrl.query(command_string, delay=0.05)
        
    def trigger_reading(self, channel, settle_time):
        self.ctrl.write('SCAN {0:d}, 0'.format(channel))
        return time.time()+settle_time # returns the time at which I can read this channel
        
    def get_temp(self, channel):
        return float(self.ctrl.query('RDGK? {0:d}'.format(channel)))
    
    def get_resistance(self, channel):
        return float(self.ctrl.query('RDGR? {0:d}'.format(channel)))
        
    def get_power(self, channel):
        return float(self.ctrl.query('RDGPWR? {0:d}'.format(channel)))
            
    def configure_from_file(self, filename):
        """ configure scanner channel using configuration file 
        
            parameters -- 
            
                channel number = which scanner channel
                
                dwell = autoscale dwell time 1-200s
                pause = value for change pause time 3-200s
                curve = temperature curve number to use 1-20, 0 for none
                tempco = temperature coefficient for temp control without curve
                
                display location = where this temperature appears on the LS display
                units = what units the display will be in 
                        Kelvin, Ohms, linear data, minimum data, maximum data
                resolution = number of digits to display
                
                excitation mode = Voltage or Current
                excitation = excitation magnitude
                             put in a float and this will round to the nearest setpoint
                range = resistance range, put in a float and this will round up to 
                        the nearest setpoint
                autorange = On (1) or Off (0)
                cs off = excitation on (0) or off (1) 
                
                filter = use filtering on(1) or off(0)
                settle time = settling time for the filter, 1 to 200 s
                window = filter window, 1-80% """
                
        with open(filename, 'r') as f:
            config = json.load(f)

        # setup channel
        self.ctrl.write('INSET {0:d}, {1:d}, {2:d}, {3:d}, {4:d}, {5:d}'.format(
                        config['channel number'], 1, config['dwell'], config['pause'],
                        config['curve'], config['tempco']))
        time.sleep(0.1)

        # setup display        
        self.ctrl.write('DISPLOC {0:d}, {1:d}, {2:d}, {3:d}'.format(
                        config['display location'], config['channel number'], 
                        units.index(config['units'])+1, config['resolution']))
        time.sleep(0.1)
        
        if config['excitation mode']=='Voltage':
            excite = np.abs(voltages - config['excitation']).argmin()+1
        elif config['excitation mode'] == 'Current':
            excite = np.abs(currents - config['excitation']).argmin()+1
        else:
            excite = np.abs(voltages - config['excitation']).argmin()+1
        rrange = ((resistances - config['range']) > 0).argmax()+1
        
        # setup excitation and reading ranges
        self.ctrl.write('RDGRNG {0:d}, {1:d}, {2:d}, {3:d}, {4:d}, {5:d}'.format(
                        config['channel number'], mode.index(config['excitation mode']), 
                        excite, rrange, config['autorange'], config['cs off']))
        time.sleep(0.1)
        
        # setup filter
        self.ctrl.write('FILTER {0:d}, {1:d}, {2:d}, {3:d}'.format(
                        config['channel number'], config['filter'], 
                        config['settle time'], config['window']))            
        time.sleep(0.1)
        
        settling_time = 3.2 # manual says 3.0, timing it says i'm missing 0.2s
        if config['filter']==1:
            settling_time += config['settle time']
        elif config['filter']==0:
            settling_time += 0.5
        
        return settling_time # return the settling time for this channel
                
    def configure_global(self, global_config, start_ch=1):
        """ configure all parameters/channels using global configuration file. """
        
        with open(global_config, 'r') as f:
            config = json.load(f)
            
        freq = np.abs(frequencies - config['frequency']).argmin()+1
        
        # display
        self.ctrl.write('DISPLAY {0:d}'.format(len(config['connected channels'])))
        time.sleep(0.1)
        
        # frequency
        self.ctrl.write('FREQ {0:d}'.format(freq))
        time.sleep(0.1)
        
        settling_times = [0 for i in range(len(config['connected channels']))]
        for i in range(1,17):
            if i in config['connected channels']:
                idx = config['connected channels'].index(i)
                channel_config = config['config files'][idx]
                head, tail = os.path.split(global_config)
                settling_times[idx] = self.configure_from_file(os.path.join(head, channel_config))
            else:
                self.ctrl.write('INSET {0:d}, 0, 2, 3, 0, 1'.format(i))
                time.sleep(0.1)
            
        self.ctrl.write('SCAN {0:d}, {1:d}'.format(start_ch, config['autoscan']))
        return settling_times