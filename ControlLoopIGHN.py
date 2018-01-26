import serial
import time
import datetime
import igh
import ilm
import qweb

#### Read/Write/Log Functions ####

def readEverything(ctrl):
    state = ''
    state += 'ighn_temp_1k=' + str(ctrl.getOneKPotTemp())
    state += ';ighn_temp_sorb=' + str(ctrl.getSorbTemp())
    state += ';ighn_temp_mix=' + str(ctrl.getMixChTemp())
    state += ';ighn_power_mix=' + str(ctrl.getMixChPower())
    state += ';ighn_power_still=' + str(ctrl.getStillPower())
    state += ';ighn_power_sorb=' + str(ctrl.getSorbPower())
    state += ';ighn_pres_g1=' + str(ctrl.getG1())
    state += ';ighn_pres_g2=' + str(ctrl.getG2())
    state += ';ighn_pres_g3=' + str(ctrl.getG3())
    state += ';ighn_pres_p1=' + str(ctrl.getP1())
    state += ';ighn_pres_p2=' + str(ctrl.getP2())
    state += ';ighn_nv=' + str(ctrl.getNV())
    state += ';ighn_v6=' + str(ctrl.getV6())
    state += ';ighn_v12a=' + str(ctrl.getV12A())    
    state += ';ighn_valves=' + str(ctrl.getStatus())
    state += ';ighn_power_mix_range=' + str(ctrl.MixPowerRange)
    ctrl.getMixChResistance() # not logging this?
    return state

def readILM(ctrl):
    ctrl.getHeliumLevel()
    ctrl.getNitrogenLevel()

def log(igh_ctrl, ilm_ctrl):
    response = qweb.getLoggableInfoForNow('igh')
    sensors = str.split(response, '\n')
    for sensor in sensors:
        if sensor != '':
            found = True
            loggable_name=''            
            props = str.split(sensor, ';')
            for prop in props:
                keyvals = str.split(prop, '=')
                if keyvals[0]=='loggable_name':
                    loggable_name = keyvals[1]
            
            # IGH North
            if loggable_name == 'ighn_temp_sorb':
                val = igh_ctrl.SorbTemp
            elif loggable_name == 'ighn_temp_1k':
                val = igh_ctrl.OneKPotTemp
            elif loggable_name == 'ighn_temp_mix':
                val = igh_ctrl.MixChTemp
            elif loggable_name == 'ighn_power_mix':
                val = igh_ctrl.MixChPower
            elif loggable_name == 'ighn_power_still':
                val = igh_ctrl.StillPower
            elif loggable_name == 'ighn_power_sorb':
                val = igh_ctrl.SorbPower
            elif loggable_name == 'ighn_pres_g1':
                val = igh_ctrl.G1
            elif loggable_name == 'ighn_pres_g2':
                val = igh_ctrl.G2
            elif loggable_name == 'ighn_pres_g3':
                val = igh_ctrl.G3
            elif loggable_name == 'ighn_pres_p1':
                val = igh_ctrl.P1
            elif loggable_name == 'ighn_pres_p2':
                val = igh_ctrl.P2
            elif loggable_name == 'ighn_nv':
                val = igh_ctrl.NV
            elif loggable_name == 'ighn_res_mix':
                val = igh_ctrl.MixChResistance
                
            #ILM
            elif loggable_name == 'bluedewar_he_level':
                val = ilm_ctrl.HeliumLevel
            elif loggable_name == 'bluedewar_ni_level':
                val = ilm_ctrl.NitrogenLevel
            else:
                found = False
                
            if found:
                qweb.makeLogEntry(loggable_name, val)
                # print(str(datetime.datetime.now()) + ': logged new data')


def executeCommands(ctrl):
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

            print(datetime.datetime.now(), ' COMMAND :: ', cmdrow)
            try:
                response = ctrl.runCommand(cmd)
                print(datetime.datetime.now(), ' RESPONSE :: ', response)
                qweb.setCommandStatus(command_id, 'P')
                qweb.setCommandResponse(command_id, response)
            except Exception as e:
                qweb.setCommandStatus(command_id, 'F')
                print(datetime.datetime.now(), 'CMD ERROR: ', e)



#### Main Control Loop ####

if __name__ == "__main__":

    port_id=2 # port_id for the qdot-server database (IGHN = 2)

    #setup period for logging/executing IGH commands
    period_all = 0.500 #seconds
    period_log = 10
    period_command = 5
    
    t_all = 0
    t_log = 0
    t_command = 0

    igh_ctrl = igh.IGH('/dev/ttyS6', 9600, 5) 
    ilm_ctrl = ilm.ILM('/dev/ttyS6', 9600, 6)

    while True:
        try:
            if time.time() - t_all >=period_all:
                state = readEverything(igh_ctrl)
                readILM(ilm_ctrl)
                t_all = time.time()
                qweb.setCurrentState(2, state)
                        
            if time.time() - t_log >=period_log:
                log(igh_ctrl, ilm_ctrl)
                t_log = time.time()
            
            if time.time() - t_command >= period_command and period_command > 0:
                executeCommands(igh_ctrl)           
                t_command = time.time()
                        
        except Exception as e:
            print(datetime.datetime.now(), ': ',e)
        time.sleep(0.1)
