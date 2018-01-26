# valve control logging

import os
from datetime import datetime, date, timedelta

class ValveControlFromFile():
	""" log data from bluefors log files into Mohammed's database """
	def __init__(self, log_dir):

		self.vc_log_dir = log_dir
		
	def _update_dates(self):
		""" update date and directory names"""
		
		# get today's date string
		self.datestr = date.today().strftime("%y-%m-%d")
		
		# get today's log directories
		self.vc_today_dir = os.path.join(self.vc_log_dir, self.datestr)
		
		# self.filelist = [os.path.join(vc_today_dir, n+'{0}.log'.format(datestr)) for n in vc_names]
		
	def _get_latest_log(self, filename):
		""" get the most recent reading from filename """
		with open(filename, 'r') as f:
			log_list = f.readlines()[-1].strip().split(',')
		timestr = ' '.join(log_list[0:2])
		return datetime.strptime(timestr, '%d-%m-%y %H:%M:%S'), log_list[2:]
	
	def get_valvecontrol_channels_logs(self):
		""" get valuecontrol panel status """
		log_file = os.path.join(self.vc_today_dir, 'Channels {0}.log'.format(self.datestr)) # get log file name
		if not os.path.isfile(log_file): # if a log file does not exist for today... 
										 # use most recent log file
			days = 1
			while days<90: # if there are no log files from the last 90 days, let it fail
				logdate = date.today() - timedelta(days)
				logdate_str = logdate.strftime("%y-%m-%d")
				vc_old_dir = os.path.join(self.vc_log_dir, logdate_str)
				log_file = os.path.join(vc_old_dir, 'Channels {0}.log'.format(logdate_str))
				if os.path.isfile(log_file):
					break
				else: 
					days += 1
		log_time, log_list = self._get_latest_log(log_file) # get most recent reading and time
		return [[log_time, log_list[i+1].strip(), float(log_list[i+2])] for i in range(0, len(log_list)-1, 2)]
	
	def get_flowmeter_logs(self):
		""" get values from flowmeter logs """
		log_file = os.path.join(self.vc_today_dir, 'Flowmeter {0}.log'.format(self.datestr)) # get log file name
		log_time, log_list = self._get_latest_log(log_file) # get most recent reading and time
		return [[log_time, 'flowmeter', float(log_list[0])]]
	
	def get_maxigauge_logs(self):
		""" get pressure values from maxigauge log file """
		log_file = os.path.join(self.vc_today_dir, 'maxigauge {0}.log'.format(self.datestr)) # get log file name
		log_time, log_list = self._get_latest_log(log_file) # get most recent reading and time
		return [[log_time, log_list[i+1].strip(), float(log_list[i+3])] for i in range(0, len(log_list)-1, 6)]
		
	def get_valvecontrol_status_logs(self):
		""" get values from valvecontrol status log file """
		log_file = os.path.join(self.vc_today_dir, 'Status_{0}.log'.format(self.datestr)) # get log file name
		log_time, log_list = self._get_latest_log(log_file) # get most recent reading and time
		return [[log_time, log_list[i].strip(), float(log_list[i+1])] for i in range(0, len(log_list), 2)]
		
	def read_all(self):
		self._update_dates() # has to come before any mention of the logs functions
		
		logging_funcs = [self.get_valvecontrol_channels_logs,
						 self.get_flowmeter_logs,
						 self.get_maxigauge_logs,
						 self.get_valvecontrol_status_logs]
			
		all_logs = []	
		for func in logging_funcs:
			try:
				all_logs += func()
			except Exception as e:
				print('ERROR in {0}: {1} at {2}'.format(func.__name__, e, str(datetime.now())))
		return all_logs
		