import urllib.request as ur
import ssl
from socket import gethostname

if gethostname=='qdot-server':
    srvUri = "https://localhost:8080/webService"
else:
    srvUri = "https://qdot-server.phas.ubc.ca:8080/webService"

    
def sendRequest(url):
        gcontext = ssl._create_unverified_context()
        response = ur.urlopen(url, context=gcontext)
        return response.read().decode('utf-8')

def sendAsync(url):
        return url
        
def makeLogEntry(loggable_name, log_value):
        url = srvUri + "/logger.php?"
        url += "action=makeLogEntry"
        url += "&loggable_name="+loggable_name
        url += "&log_value="+str(log_value)
        return sendRequest(url)

def getLoggableInfoForNow(machine_type):
        url = srvUri + "/logger.php?action=getLoggableInfoForNow&machine_type="+machine_type
        return sendRequest(url)

def lock(port_id, locked_by):
        url = srvUri + "/logger.php?action=lockport&port_id="+str(port_id)+"&locked_by="+locked_by
        return sendRequest(url)

def unlock(port_id, locked_by):
        url = srvUri + "/logger.php?action=unlockport&port_id="+str(port_id)+"&locked_by="+locked_by
        return sendRequest(url)

def setCurrentState(loggable_category_id, state):
        url = srvUri + "/logger.php?action=setCurrentState&loggable_category_id=" + str(loggable_category_id) + "&state=" + state
        return sendRequest(url)

def createCommand(port_id, cmd):
        url = srvUri + "/commandmanager.php?action=createCommand&port_id="+str(port_id)+"&cmd="+cmd
        return sendRequest(url)

def getCommands(port_id, status):
        url = srvUri + "/commandmanager.php?action=getCommands&port_id="+str(port_id)+"&status="+status
        return sendRequest(url)

def setCommandStatus(command_id, status):
        url = srvUri + "/commandmanager.php?action=setCommandStatus&command_id="+str(command_id)+"&status="+status
        return sendRequest(url)

def setCommandResponse(command_id, response):
        url = srvUri + "/commandmanager.php?action=setCommandResponse&command_id="+str(command_id)+"&response="+response
        return sendRequest(url)
        
def getConfig(config_name):
        url = srvUri + "/logger.php?action=getConfig&config_name="+config_name
        return sendRequest(url)

def getCurrentState(port_id):
        url = srvUri + "/logger.php?action=getCurrentState&loggable_category_id="+str(port_id)
        return sendRequest(url)
