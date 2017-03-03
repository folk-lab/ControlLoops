import lakeshore
import magheater
import json
import qweb
from datetime import datetime, timedelta
import time
import math
import re
import os

### dictionaries to map log file names to database names ###

# pairs are (local_name: loggable_name)
name_reference = {'CH1 P': None,
                  'CH1 R': None,
                  'CH1 T': 'bfs_50K_temp',
                  'CH2 P': None,
                  'CH2 R': None,
                  'CH2 T': 'bfs_4K_temp',
                  'CH4 P': None,
                  'CH4 R': None,
                  'CH4 T': 'bfs_magnet_temp',
                  'CH5 P': None,
                  'CH5 R': None,
                  'CH5 T': 'bfs_still_temp',
                  'CH6 P': None,
                  'CH6 R': 'bfs_mc_r',
                  'CH6 T': 'bfs_mc_temp',
                  'a1_u': None,
                  'a1_r_lead': None,
                  'a1_r_htr': None,
                  'a2_u': 'bfs_still_heater',
                  'a2_r_lead': None,
                  'a2_r_htr': None,
                  'htr': 'bfs_mc_heater',
                  'htr_range':  None}
                  
# pairs are (loggable_name: local_name)
inv_name_reference = {v: k for k, v in name_reference.items() if v}

### functions to deal with all of the lakeshore logging ###

def read_all_values(ctrl):

    htr_ranges = {0:0.0, 1:31.6e-6, 2:100e-6, 3:316e-6, 4:1.00e-3,
                5:3.16e-3, 6:10.0e-3, 7:31.6e-3, 8:100e-3} 
    still_R = 120.0
    still_leads = 30.0
    mc_R = 120.0
    mc_leads = 0.0
    
    # get still power in mW
    still_volts = (float(ctrl.query('STILL?'))/100.0)*10.0
    still_current = still_volts/(still_leads+still_R)
    still_power = still_current**2*(still_R+still_leads)*1000.0
    
    # get mixing chamber power in mW
    mc_out = float(ctrl.query('MOUT?'))/100.0 
    cset = ls.query('CSET?').strip().split(',')
    htrrng = int(ctrl.query('HTRRNG?'))
    if cset[4]=='1': # current mode
        mc_current = htr_ranges[htrrng]*mc_out
        mc_power = mc_current**2*(mc_R)*1000.0
    else: # power mode
        mc_power = mc_out*1000.0 # in mW
    
    n = len(sensor_data)
    sdata = [[] for i in range(n+8)]
    sdata[0:n] = sensor_data
    sdata[n+0] = [datetime.now(), 'a1_u', float(ls.query('ANALOG? 1').split(',')[-1])] # not used currently
    sdata[n+1] = [datetime.now(), 'a1_r_lead', 0.0]
    sdata[n+2] = [datetime.now(), 'a1_r_htr', 0.0]
    sdata[n+3] = [datetime.now(), 'a2_u', still_power] # in mW
    sdata[n+4] = [datetime.now(), 'a2_r_lead', still_leads]
    sdata[n+5] = [datetime.now(), 'a2_r_htr', still_R]
    sdata[n+6] = [datetime.now(), 'htr', mc_power] # in mW
    sdata[n+7] = [datetime.now(), 'htr_range', htrrng]
    return sdata
    
def update_single_sensor(ctrl, channel, all_data):
    global sensors
    global sensor_data 
    
    idx_data = sensors.index('CH{0} P'.format(channel))
    sensor_data[idx_data][0] = datetime.now()
    sensor_data[idx_data][2] = ctrl.get_power(channel)
    all_data[idx_data] = sensor_data[idx_data]
    sensor_data[idx_data+1][0] = datetime.now()
    sensor_data[idx_data+1][2] = ctrl.get_resistance(channel)
    all_data[idx_data] = sensor_data[idx_data]
    sensor_data[idx_data+2][0] = datetime.now()
    sensor_data[idx_data+2][2] = ctrl.get_temp(channel)
    all_data[idx_data] = sensor_data[idx_data]
    return all_data
    
### functions to handle commands ###

def update_scanner_cycle(cmd):
    # function to update scanner cycle
    # format of cmd is SCANNER t1,t2,t4,t5,t6
    
    # get list from cmd
    new_sequence = [float(t) for t in cmd[7:].strip().split(',')]
    
    # load existing config and rewrite scanner sequence
    global_config = r'C:\Users\LabUser\Documents\GitHub\ControlLoops\ls_config_bfs\global.config'
    with open(global_config, 'r') as f:
            config = json.load(f)
    config['scanner sequence'] = new_sequence
    with open(global_config, 'w') as f:
        json.dump(config, f)
    
def execute_commands(port_id, ctrl, ctrl_heat):
        response = qweb.getCommands(port_id, 'C') 
        cmdrows = str.split(response, '\n')
        for cmdrow in cmdrows:
                if cmdrow != '':
                        props = str.split(cmdrow, ';')
                        for prop in props:
                                keyvals = str.split(prop, '=')
                                if keyvals[0]=='command_id':
                                        command_id=keyvals[1]
                                elif keyvals[0]=='cmd':
                                        cmd=keyvals[1]

                        print(cmdrow)
                        try:
                                if '?' in cmd:
                                    response = ctrl.query(cmd)
                                    print(response)
                                    qweb.setCommandResponse(command_id, response)
                                elif cmd.startswith('SCANNER'):
                                    update_scanner_cycle(cmd)
                                elif cmd.startswith('MAGHEATER'):
                                    if ctrl_heat:
                                        if "on" in cmd.lower():
                                            ctrl_heat.relay_on()
                                        else:
                                            ctrl_heat.relay_off()
                                    else:
                                        print('HEATER OPERATION IGNORED: device not connected.')
                                else:
                                    ctrl.write(cmd)
                                qweb.setCommandStatus(command_id, 'P')
                        except Exception as e:
                                print('ERROR: {}'.format(str(e)))
                                qweb.setCommandStatus(command_id, 'F')
    
### functions to handle sending relevant data to the server ###

def format_state(data):
    global name_reference
    state = ''
    for d in data:
        state+='{0}={1};'.format(name_reference[d[1]], d[2])
    return state
    
def find_included_names(data):
    """ take all log data read and return only those that have database entries """
    global name_reference
    loggable_data = []
    for d in data:
        if name_reference[d[1]]:
            loggable_data.append(d)
    return loggable_data
    
def find_loggable_data(data):
    """ ask the server what needs to be updated. return just that list """
    # get string from server describing which parameters need to be updated
    global inv_name_reference
    
    # string describing what needs to be updated
    loggable_str = qweb.getLoggableInfoForNow('bfs')
    # list of loggable_names to be updated 
    loggable_list = re.findall(r'loggable_name=(\w+);',loggable_str)
    
    loggable_data = []
    if loggable_list:
        # get list of bluefors names from loggable_list using dictionary
        lookup_list = [inv_name_reference[k] for k in loggable_list if k in inv_name_reference]
        for d in data:
            if d[1] in lookup_list:         
                loggable_data.append(d)
    return loggable_data

def log_new_data(data):
    """ push new database entries to the sql database using
        the web service """
    for d in data:
        qweb.makeLogEntry(name_reference[d[1]], d[2])

### main loop below ###

def check_dts(settling_time, sequence):
    for i in range(len(sequence)):
        if settling_time[i]>sequence[i]:
            sequence[i]=settling_time[i]
    return sequence

def pick_channel(channels, sequence, tcurrent):
    global sensor_data
    
    # get a list of just the temperature reading times
    dt_temp = []
    for i in range(2,len(sensor_data),3):
        dt_temp.append((tcurrent-sensor_data[i][0]).total_seconds())
    dt = [dt_temp[i]-sequence[i] for i in range(len(dt_temp))]
    idx = dt.index(max(dt))
    return idx, channels[idx]

if __name__ == "__main__":
    global sensors
    global sensor_data
    
    sensors = []
    sensor_data = []
    for key in name_reference:
         if key.startswith('CH'):
            sensors.append(key)
    sensors = sorted(sensors, key=lambda x: (x[2], x[-1])) # use this to find index
    sensor_data = [[datetime.now(), s, 0.0] for s in sensors] # use this to store data
    
    config_file = r'C:\Users\LabUser\Documents\GitHub\ControlLoops\ls_config_bfs\global.config'
    config_time = os.path.getmtime(config_file)
    with open(config_file, 'r') as f: # fix config file paths
        config = json.load(f)
                
    channels = config['connected channels'] 
    channel_cycle = config['scanner sequence'] # list of read times in seconds

    ls_port = config['ls_port']
    heater_port = config['heater_port']
    ls = lakeshore.LS370(ls_port, interface='Serial')
    if heater_port < 0:
        heat = None
        print('Magnet Heater not connected')
    else:
        heat = magheater.Heater(hetaer_port)
        
    response = ls.query('*IDN?')
    if response.split(',')[1]!='MODEL370':
        raise IOError('Not reading the correct instrument?')
    else:
        print(response)
    settling_times = ls.configure_global(config_file)
    channel_cycle = check_dts(settling_times, channel_cycle)
    print(settling_times)
    print(channel_cycle)
    time.sleep(0.2)
    
    # fill out initial data for sensors
    junk_data = sensor_data 
    for ch in channels:
        update_single_sensor(ls, ch, junk_data)
    
    # information for database
    port_id = 3
    loggable_category_id = 4

    while True:
        strt = time.time()
        
        # look for a new scanner sequence
        if os.path.getmtime(config_file) > config_time:
            print('new config found!')
            with open(config_file, 'r') as f: # fix config file paths
                temp_config = json.load(f)
                if len(temp_config['scanner sequence'])==len(channels):
                    channel_cycle = temp_config['scanner sequence']
                    channel_cycle = check_dts(settling_times, channel_cycle)
                    print('scanner sequence updated to: {0}'.format(','.join([str(c) for c in channel_cycle])))
                config_time = os.path.getmtime(config_file)
                
        ### trigger channel reading ###
        idx, read_channel = pick_channel(channels, channel_cycle, datetime.now())
        # print('reading channel: {0}'.format(read_channel))
        
        current_channel = int(ls.query('SCAN?').split(',')[0])
        if current_channel != read_channel:
            read_time = ls.trigger_reading(read_channel, settling_times[idx])
        else:
            read_time= time.time()
       
        ### do other stuff while waiting for reading to settle ###
        
        execute_commands(port_id, ls, heat) # execute any commands
        data = read_all_values(ls) # grab most recent sensor data
        
        # log values to server
        strt = time.time()
        ldata = find_included_names(data)
        state = format_state(ldata)
        qweb.setCurrentState(loggable_category_id, state)
        new_data = find_loggable_data(ldata)
        if new_data:
            log_new_data(new_data)
            print('new data logged! {0}'.format(str(datetime.now())))
        
        ### go back and get the new sensor reading ###
        
        while(time.time()<read_time): 
            # wait here for the reading to settle
            pass
        data = update_single_sensor(ls, read_channel, data)
        # print('Logged: {0:d} values, Loop time: {1:.3f}s'.format(len(new_data), time.time()-strt))