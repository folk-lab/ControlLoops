import serial
import io
import time
import datetime
import sys
import igh
import qweb

#### Read/Write/Log Functions ####

def ReadEverything(igh):
	state = ''
	state += 'ighn_temp_1k=' + str(igh.GetOneKPotTemp())
	state += ';ighn_temp_sorb=' + str(igh.GetSorbTemp())
	state += ';ighn_temp_mix=' + str(igh.GetMixChTemp())
	state += ';ighn_power_mix=' + str(igh.GetMixChPower())
	state += ';ighn_power_still=' + str(igh.GetStillPower())
	state += ';ighn_power_sorb=' + str(igh.GetSorbPower())
	state += ';ighn_pres_g1=' + str(igh.GetG1())
	state += ';ighn_pres_g2=' + str(igh.GetG2())
	state += ';ighn_pres_g3=' + str(igh.GetG3())
	state += ';ighn_pres_p1=' + str(igh.GetP1())
	state += ';ighn_pres_p2=' + str(igh.GetP2())
	state += ';ighn_nv=' + str(igh.GetNV())
	state += ';ighn_v6=' + str(igh.GetV6())
	state += ';ighn_v12a=' + str(igh.GetV12A())	
	state += ';ighn_valves=' + str(igh.GetStatus())
	state += ';ighn_power_mix_range=' + str(igh.MixPowerRange)
	igh.GetMixChResistance()
	return state

def Log(igh, ilm):
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
			
			# IGH North and South
			if loggable_name == 'ighn_temp_sorb':
				val = igh.SorbTemp
			elif loggable_name == 'ighn_temp_1k':
				val = igh.OneKPotTemp
			elif loggable_name == 'ighn_temp_mix':
				val = igh.MixChTemp
			elif loggable_name == 'ighn_power_mix':
				val = igh.MixChPower
			elif loggable_name == 'ighn_power_still':
				val = igh.StillPower
			elif loggable_name == 'ighn_power_sorb':
				val = igh.SorbPower
			elif loggable_name == 'ighn_pres_g1':
				val = igh.G1
			elif loggable_name == 'ighn_pres_g2':
				val = igh.G2
			elif loggable_name == 'ighn_pres_g3':
				val = igh.G3
			elif loggable_name == 'ighn_pres_p1':
				val = igh.P1
			elif loggable_name == 'ighn_pres_p2':
				val = igh.P2
			elif loggable_name == 'ighn_nv':
				val = igh.NV
			elif loggable_name == 'ighn_res_mix':
				val = igh.MixChResistance
			#ILM
			elif loggable_name == 'bluedewar_he_level':
				val = ilm.HeliumLevel
			elif loggable_name == 'bluedewar_ni_level':
				val = ilm.NitrogenLevel
			else:
				found = False
				
			if found:
				qweb.makeLogEntry(loggable_name, val)


def ReadILM(ilm):
	ilm.GetHeliumLevel()
	ilm.GetNitrogenLevel()


def ExecuteCommands():
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
				response = igh.RunCommand(cmd)
				print(datetime.datetime.now(), ' RESPONSE :: ', response)
				qweb.setCommandStatus(command_id, 'P')
				qweb.setCommandResponse(command_id, response)
			except:
				qweb.setCommandStatus(command_id, 'F')



#### Main Control Loop ####

if __name__ == "__main__":

    port_id=2

    period_all = 0.500 #seconds
    period_log = 15
    period_readConfig = 10
    period_command = 5

    AllowReadAll = True

    igh_ctrl = igh.IGH(port_id, '/dev/ttyS6', 9600, 5, 'ighcontroller') 
    ilm_ctrl = igh.IGH(port_id, '/dev/ttyS6', 9600, 6, 'ighcontroller')

    t_all = 0
    t_log = 0
    t_readConfig = 0
    t_adjNV = 0
    t_command = 0

    while True:
        try:
            if time.time() - t_all >=period_all and AllowReadAll:
                state = ReadEverything(igh)
                ReadILM(ilm_ctrl)
                t_all = time.time()
                qweb.setCurrentState(2, state)
                        
            if time.time() - t_log >=period_log and AllowReadAll:
                Log(igh_ctrl, ilm_ctrl)
                t_log = time.time()
            
            if time.time() - t_command >= period_command and period_command > 0:
                ExecuteCommands()			
                t_command = time.time()
                        
        except Exception as e:
            print(datetime.datetime.now(), ': ',e)