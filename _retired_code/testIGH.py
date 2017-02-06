import igh
import time
igh_ctrl = igh.IGH(2, '/dev/ttyS6', 9600, 7, 'testIGH')
#t = time.time()
#print igh.GetG1()
#ReadEverything(igh)
#print igh.GetOneKPotTemp()
#print(igh.RunCommand('C3'))
#print igh.RunCommand('A0')
#print(igh.SetIsobusAddress(7))
print(igh_ctrl.GetHeliumLevel())
#print(igh.GetMixChPower())
#print('Mixing Chamber Power is '+str(igh.GetMixChPower()))
#output = igh.RunCommand('X')
#X = int(output[1:2])
#A = int(output[3:4])
#C = int(output[5:6])
#P = int(output[7:15], 16) # Converts a base 16 (hex) string to an integer
#S = int(output[16:17])
#O = int(output[18:19])
#E = int(output[20:21])
#
#print "E: ", E

#r = p*pow(10,E-4)
#print "Mixing Chamber Power is ", r, "uW"
