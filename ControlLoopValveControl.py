import valvecontrol
import qweb
from datetime import datetime, timedelta
import time
import re

### dictionaries to map log file names to database names ###

# pairs are (local_name: loggable_name)
name_reference = {'v11': None,
				  'v2': None,
				  'v1': None,
				  'turbo1': None,
				  'v12': None,
				  'v3': None,
				  'v10': None,
				  'v14': None,
				  'v4': None,
				  'v13': None,
				  'compressor': None,
				  'v15': None, 
				  'v5': None, 
				  'hs-still': 'bfs_still_heatswitch',
				  'v21': None, 
				  'v16': None, 
				  'v6': None, 
				  'scroll1': None, 
				  'v17': None, 
				  'v7': None, 
				  'scroll2': None, 
				  'v18': None, 
				  'v8': None, 
				  'pulsetube': None, 
				  'v19': None, 
				  'v20': None, 
				  'v9': None, 
				  'hs-mc': 'bfs_mc_heatswitch', 
				  'ext': None, 
				  'flowmeter': 'bfs_flowmeter', 
				  'P1  ': 'bfs_p1', 
				  'P2  ': 'bfs_p2', 
				  'P3  ': 'bfs_p3', 
				  'P4  ': 'bfs_p4', 
				  'P5  ': 'bfs_p5', 
				  'P6'  : 'bfs_p6', # this is a little messed up
				  'cptempwi': 'bfs_cmp_tempwi', 
				  'cptempwo': 'bfs_cmp_tempwo', 
				  'cptemph': None, 
				  'cptempo': 'bfs_cmp_tempo',
				  'cpttime': None,
				  'cperrcode': None,
				  'cpavgl': None,
				  'cpavgh': None,
				  'nxdsf': None,
				  'nxdsct': None,
				  'nxdst': None,
				  'nxdsbs': None,
				  'nxdstrs': None,
				  'tc400p': None,
				  'tc400errorcode': None,
				  'tc400ovtempelec': None,
				  'tc400ovtemppump': None,
				  'tc400setspdatt': None,
				  'tc400pumpaccel': None,
				  'tc400commerr': None,
				  'ctrl_pres': None}
		
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
	
# using threading.Timer() is probably the right way to do it, but it 
# needs a little more work

if __name__ == "__main__":
	vc = valvecontrol.ValveControlFromFile()
	while True:
		try:
			data = find_included_names(vc.read_all())
			new_data = find_loggable_data(data)
			if new_data:
				print('new data logged! {0}'.format(str(datetime.now())))
				log_new_data(new_data)
		except Exception as e:
			print('ERROR: {0} at {1}'.format(e, str(datetime.now())))
		time.sleep(loop_time)