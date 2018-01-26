# ControlLoops

Instrument control scripts to handle logging/communication

Philosopy:

Each piece of equipment is controlled by one computer/RaspberryPi. That piece of equipment should have two associated scripts.

1. instrument.py -- controls the instrument on the local machine over serial/GPIB. should not rely on qweb.
2. ControlLoopINSTRUMENT.py -- handles access to the machine. probably runs some horrible infinite loop.

## Currently Running:

qdot-server -- ControlLoopIGHN (background process), ControlLoopXBee (background process), measurement_data_sync (cronjob: 1/day)

Switching over to InfluxDB right now. Trying to keep all processes running on server. 
