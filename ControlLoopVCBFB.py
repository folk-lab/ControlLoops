import valvecontrol
import qweb
from datetime import datetime, timedelta
import time
import re

### dictionaries to map log file names to database names ###

# pairs are (local_name: loggable_name)
name_reference = {
'v11': None,
'v2': None,
'v1': None,
'turbo1': None,
'v12': None,
'v3': None,
'v10': None,
'turbo2': None,
'v14': None,
'v4': None,
'v13': None,
'compressor': None,
'v15': None,
'v5': None,
'hs-still': 'bfb_still_heatswitch',
'v21': None,
'v16': None,
'v6': None,
'scroll1': None,
'v22': None,
'v17': None,
'v7': None,
'scroll2': None,
'v23': None,
'v18': None,
'v8': None,
'pulsetube': None,
'v19': None,
'v20': None,
'v9': None,
'hs-mc': 'bfb_mc_heatswitch',
'ext': None,
'a1_u': None,
'a1_r_lead': None,
'a1_r_htr': None,
'a2_u': None,
'a2_r_lead': None,
'a2_r_htr': None,
'htr': None,
'htr_range': None,
'tc400errorcode': None,
'tc400ovtempelec': None,
'tc400ovtemppump': None,
'tc400setspdatt': None,
'tc400pumpaccel': None,
'tc400commerr': None,
'tc400errorcode_2': None,
'tc400ovtempelec_2': None,
'tc400ovtemppump_2': None,
'tc400setspdatt_2': None,
'tc400pumpaccel_2': None,
'tc400commerr_2': None,
'tvpower1': None,
'tvbearingtemp1': None,
'tvcontrollertemp1': None,
'tvbodytemp1': None,
'tvrot1': None,
'tvlife1': None,
'ctrl_pres': None,
'cpastate': None,
'cparun': None,
'cpawarn': None,
'cpaerr': None,
'cpatempwi': 'bfb_cmp_tempwi',
'cpatempwo': 'bfb_cmp_tempwo',
'cpatempo': 'bfb_cmp_tempo',
'cpatemph': None,
'cpalp': None,
'cpalpa': None,
'cpahp': None,
'cpahpa': None,
'cpadp': None,
'cpacurrent': None,
'cpahours': None,
'cpapscale': None,
'cpatscale': None,
'cpasn': None,
'cpamodel': None,
'flowmeter': 'bfb_flowmeter',
'P1': 'bfb_p1',
'P2': 'bfb_p2',
'P3': 'bfb_p3',
'P4': 'bfb_p4',
'P5': 'bfb_p5',
'P6': 'bfb_p6'
}

# pairs are (loggable_name: local_name)
inv_name_reference = {v: k for k, v in name_reference.items() if v}
			
### time constants ###

loop_time = 5.0 # seconds

### utility functions ###

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
	loggable_str = qweb.getLoggableInfoForNow('bfb')
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

if __name__ == "__main__":
	vc = valvecontrol.ValveControlFromFile(r'C:\Users\folklab101\Desktop\logs')
	# print(inv_name_reference)
	while True:
		try:
			data = find_included_names(vc.read_all())
			print('read all data...')
			new_data = find_loggable_data(data)
			if new_data:
				print('logging new data...')
				log_new_data(new_data)
				print('new data logged! {0}'.format(str(datetime.now())))
		except Exception as e:
			print('ERROR: {0} at {1}'.format(e, str(datetime.now())))
		time.sleep(loop_time)