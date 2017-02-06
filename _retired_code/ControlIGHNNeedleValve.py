import qweb
import time

port_id=2 # for IGHN

# time units are seconds
period_readConfig = 10
period_adjNV = 10 #default
t_readConfig = 0
t_adjNV = 0

p2nv_high = 30
p2nv_low = 5

p2=0
nv=-1

#### Main Control Loop ####

if __name__ == "__main__":

    while True:
        if time.time() - t_readConfig >= period_readConfig:
            period_adjNV = int(qweb.getConfig('ighn_adjnv_period'))
            nv_step = float(qweb.getConfig('ighn_nv_step'))
            p2nv_high = float(qweb.getConfig('ighn_p2nv_high'))
            p2nv_low = float(qweb.getConfig('ighn_p2nv_low'))
            t_readConfig = time.time()
        if time.time() - t_adjNV >= period_adjNV and period_adjNV > 0:
            cmd=""
            stateString = qweb.getCurrentState(port_id)
            sArray = stateString.split(';')
            for s in sArray:
                if s[0:12] == 'ighn_pres_p2':
                    p2 = float(s.split('=')[1])
                elif s[0:7] == 'ighn_nv':
                    nv = float(s.split('=')[1])
    
            if p2>p2nv_high and nv!=-1:
                #print "p2>p2nv_high"
                nv -= nv_step
                cmd="N"+str(int(nv*10))
            elif p2<p2nv_low and nv!=-1:
                #print "p2<p2nv_low"
                nv += nv_step
                cmd="N"+str(int(nv*10))
        
            if cmd!="":
                #print cmd
                qweb.createCommand(port_id, 'C3') # Set IGH to remote mode
                qweb.createCommand(port_id, cmd)
        
            t_adjNV = time.time()
    
        time.sleep(1.0)
