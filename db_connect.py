from influxdb import InfluxDBClient
from datetime import timezone, datetime
from random import random
import time, pytz

class InfluxClient(InfluxDBClient):
    def __init__(self):
        self.host = 'qdot-server.phas.ubc.ca'
        self.port = 8086
        self.dbname = 'test'
        self.timezone = pytz.timezone('America/Vancouver')
        InfluxDBClient.__init__(self,
            host=self.host, port=self.port, database=self.dbname)
    def log_float(self, tags, timestamp, value, 
                    field="val", measurement="experiment"):
        ''' tags (dict) -> identifying information to log with value
                    examples == label: bfs_P1
                                component: lksh370
            field (str) -> type of measurement (power, pressure, volts...)
                           defaults to val
            timestamp (datetime.datetime) -> timestamp for measurement
            value(float) -> value to log 
            measurement (str) -> not sure how best to use this. 
                                 defaults to 'experiment' '''
        localstamp = self.timezone.localize(timestamp)
        json_body = [
            {
                "measurement": measurement, 
                "time": localstamp,
                "tags": tags,
                "fields": {
                    field: value,
                },
            }
        ]
        self.write_points(json_body)


# def main(n, host='localhost', port=8086, dbname='test'):
#     """ open a connection and push random numbers until KeyBoard interrupt """
#     client = InfluxClient()
#
#     for i in range(n):
#         tags = {
#             'label': 'influx_test', 
#             'component': 'random_num',
#         }
#         client.log_float(tags, datetime.now(), random())
#         print('wrote: ', i)
#         time.sleep(5.0)
#    
#     return None

