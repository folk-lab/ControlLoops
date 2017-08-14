import serial
import time

EOL = '\r'  # End of line character for the IGH
valve_map = {
    'V9':       1,
    'V8':       2,
    'V7':       3,
    'V11A':     4,
    'V13A':     5,
    'V13B':     6,
    'V12B':     7,
    'He4Rot':   9,
    'V1':       10,
    'V5':       11,
    'V4':       12,
    'V3':       13,
    'V14':      14,
    'V10':      15,
    'V2':       16,
    'V2A':      17,
    'V1A':      18,
    'V5A':      19,
    'V4A':      20,
    'V3A':      21,
    'Roots':    22,
    'He3Rot':   24
}

class IGH:
    # Constructor. This is called when an object of type IGH is created.
    # Example obj = IGH('/dev/ttyS1', 9600, 5)
    # This example will create an instance of the IGH class called obj which can be used to talk to IGNHN (isobus#5)
    # Owner is the process that made the object. It should be a name unique to a process that is used to lock the serial port.
    def __init__(self, port_name, baudrate, machine_id):
        self.serial_port = serial.Serial(port_name, baudrate=baudrate, timeout=1, stopbits=2)
        self.machine_id = machine_id # this is the ISOBUS address
    
    def __del__(self):
        self.serial_port.close()
    
    # ATTENTION:    Don't use this when several ISOBUS devices are connected and powered on
    # ALSO:         Don't forget to save the changes into the permanent memory after running this function
#   def setIsobusAddress(self, address):
#       response = ''
#       to_write = 'U1!{:d}{}'.format(address, EOL)
#       wrote = self.serial_port.write(to_write.encode('latin1'))
#       ch = ''
#       t = time.time()         # Don't try to read forever, if there's nothing
#       while ch != EOL and time.time() - t < 1:
#           ch = self.serial_port.read().decode('utf-8')
#           response += ch
#       self.serial_port.flush()
# 
#       to_write = 'U0{}'.format(EOL)
#       wrote = self.serial_port.write(to_write.encode('latin1'))
#       ch = ''
#       t = time.time()         # Don't try to read forever, if there's nothing
#       while ch != EOL and time.time() - t < 1:
#           ch = self.serial_port.read().decode('utf-8')
#           response += ch
#       self.serial_port.flush()        
#       
#       self.machine_id = address
#       return response
        
    def runCommand(self, cmd):
        
        response = ''

        # commands to increment valves
        if cmd[0:2]=='NV':
            if cmd[2]=='-':
                a = -1.0
            elif cmd[2]=='+':
                a = 1.0
            else:
                raise ValueError('ILL-FORMATED COMMAND: {0:s}'.format(cmd))
            val = self.NV+a*float(cmd[3:])
            print('NV being set to: {0:.2f}'.format(val))
            response = self.setValve('NV', val)
            return response     

        to_write = '@{:d}{}{}'.format(self.machine_id, cmd, EOL)
        if not self.serial_port.isOpen():
            self.serial_port.open()

        self.dirty = 1
        
        wrote = self.serial_port.write(to_write.encode('latin1'))
        if wrote != len(to_write):
            raise ValueError('SERIAL WRITE FAILED: ', cmd)
        
        t = time.time() # Don't try to read forever, if there's nothing
        ch = ''
        while ch != EOL and time.time() - t < 1.0:
            ch = self.serial_port.read().decode('utf-8')
            response += ch
    
        self.serial_port.flush()
        # if cmd[:1] == 'N':
        #     print('To Write: ', to_write)
        if response[:1] == '?':
            raise ValueError('IGH RESPONSE ERROR: {0:s}, {1:s}', response, cmd)
        return response

    def getStatus(self):
        output = self.runCommand('X').strip()
        X = int(output[1:2])
        A = int(output[3:4])
        C = int(output[5:6])
        P = int(output[7:15], 16) # Converts a base 16 (hex) string to an integer
        S = int(output[16:17])
        O = int(output[18:19])
        E = int(output[20:21])
        
        self.MixPowerOnOff = A
        self.MixPowerRange = E
        
        self.Remote = C&1
        self.Unlocked = (C&2)/2
        
        self.V1=(P & 2**9)/2**9
        self.V2=(P & 2**15)/2**15
        self.V3=(P & 2**12)/2**12
        self.V4=(P & 2**11)/2**11
        self.V5=(P & 2**10)/2**10
        self.V7=(P & 2**2)/2**2
        self.V8=(P & 2**1)/2**1
        self.V9=(P & 2**0)/2**0
        self.V10=(P & 2**14)/2**14
        self.V11A=(P & 2**3)/2**3
        self.V11B=(P & 2**6)/2**6
        self.V12B=(P & 2**7)/2**7
        self.V13A=(P & 2**4)/2**4
        self.V13B=(P & 2**5)/2**5
        self.V14=(P & 2**13)/2**13
        self.V1A=(P & 2**17)/2**17
        self.V2A=(P & 2**16)/2**16
        self.V4A=(P & 2**19)/2**19
        self.V5A=(P & 2**18)/2**18
        self.PHe3=(P & 2**23)/2**23
        self.PRoots=(P & 2**21)/2**21
        self.PHe4=(P & 2**8)/2**8
        
        # TODO Set other variables that can be extracted from the 'X' string.
        # See page 28 of IGH Kelvinox Electronics 
            
        return output

    # This will return the Sorb Temperature if the current isobus machine_id corresponds to an IGH
    def getSorbTemp(self):
        output = self.runCommand('R1')
        self.SorbTemp = float(output[3:])/10
        return self.SorbTemp

    # This will return the 1K Pot Temperature if the current isobus machine_id corresponds to an IGH
    def getOneKPotTemp(self):
        output = self.runCommand('R2')
        self.OneKPotTemp = float(output[3:])/1000
        return self.OneKPotTemp

    def getMixChTemp(self):
        output = self.runCommand('R3')
        val = float(output[3:])
        if val < 3000:
            output = self.runCommand('R32')
            val = float(output[2:])/10
        
        self.MixChTemp = val
        return val
        
    def getMixChPower(self):
        '''
        Mixing chamber power in units of micro Watts
        '''
        self.getStatus()    
        output = self.runCommand('R4')
        r = pow(10,self.MixPowerRange - 4)
        self.MixChPower = float(output[3:]) * r / 1000
        return float(float(output[3:]) * r)
        
    def getStillPower(self):
        output = self.runCommand('R5')
        self.StillPower = float(output[3:])/10
        return self.StillPower
    
    def getSorbPower(self):
        output = self.runCommand('R6')
        self.SorbPower = float(output[3:])
        return self.SorbPower

    def getV6(self):
        output = self.runCommand('R7')
        self.V6 = float(output[2:])/10
        return self.V6
        
    def getV12A(self):
        output = self.runCommand('R8')
        self.V12A = float(output[2:])/10
        return self.V12A

    def getNV(self):
        output = self.runCommand('R9')
        self.NV = float(output[2:])/10
        return self.NV
    
    def getG1(self):
        output = self.runCommand('R14')
        self.G1 = float(output[3:])/10
        return self.G1

    def getG2(self):
        output = self.runCommand('R15')
        self.G2 = float(output[3:])/10
        return self.G2

    def getG3(self):
        output = self.runCommand('R16')
        self.G3 = float(output[3:])/10
        return self.G3

    def getP1(self):
        output = self.runCommand('R20')
        self.P1 = float(output[1:])
        return self.P1

    def getP2(self):
        output = self.runCommand('R21')
        self.P2 = float(output[1:])
        return self.P2

    def getMixChResistance(self):
        output = self.runCommand('R35')
        self.MixChResistance = float(output[1:])*100
        return self.MixChResistance
    
    def setRemote(self):
        self.runCommand('C3')

    def setLocal(self):
        self.runCommand('C2')

    # ValveName='V1', "V2", "V1A"
    # For valves 'NV', "V6" and "V12A", value means percent open (0 <= value <= 100).
    # For other valves, value 1 = on, 0 = off
    def setValve(self, valve, value):
        response = ''
        try:
            self.setRemote()    
            if valve=='V6':
                response = self.runCommand('G'+round(value*10))
                self.V6 = value
            elif valve=='V12A':
                response = self.runCommand('H'+round(value*10))
                self.V12A = value
            elif valve=='NV':
                sval = '%03d' % round(value*10)
                response = self.runCommand("N"+sval)
                self.NV = value
        finally:
            self.setLocal()
            return response

    def adjustNV(self, step, P2lo, P2hi):
#       step = float(qweb.getConfig('ighn_nv_step'))
#       P2lo = float(qweb.getConfig('ighn_p2nv_low'))
#       P2hi = float(qweb.getConfig('ighn_p2nv_high'))
        self.getNV()
        #print '==================== Adjust NV ======================'
        #print time.strftime('%H:%M:%S'), "P2:", self.P2, "step:", step, "P2 Low:", P2lo, "P2 High:", P2hi, " NV:", self.NV     
        
        if self.P2 < P2lo:      # need to increase
            #print time.strftime('%H:%M:%S'), " Increase. P2:", self.P2, "step:", step, "P2 Low:", P2lo, "P2 High:", P2hi, " NV:", self.NV
            self.SetValve('NV', self.NV + step)
            #print 'Done increasing to ', self.NV + step
            #print 'Needle valve is now ', self.GetNV()
        elif self.P2 > P2hi:    # need to decrease
            #print time.strftime('%H:%M:%S'), " Decrease.  P2:", self.P2, "step:", step, "P2 Low:", P2lo, "P2 High:", P2hi, " NV:", self.NV
            self.SetValve('NV', self.NV - step)
            #print 'Done decreasing to ', self.NV - step
            #print 'Needle valve is now ', self.GetNV()
    

