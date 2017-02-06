# ControlLoops

Instrument control scripts to handle logging/communication

Philosopy:

Each piece of equipment is controlled by one computer. That piece of equipment should have two associated scripts.

1. instrument.py -- controls the instrument on the local machine over serial/GPIB. should not rely on qweb.
2. ControlLoopINSTRUMENT.py -- handles access to the machine via qweb. probably runs some horrible infinite loop.
