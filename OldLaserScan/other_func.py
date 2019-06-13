import time
import numpy as np
from numpy import loadtxt
import getpass
import os
import subprocess 
import subprocess                                                                                                                                                                                                                                                                       
from subprocess import Popen, PIPE                                                                                                                                                                                                                                                      
import pipes                                                                                                                                                                                                                                                                            
from pipes import quote  
import socket
import sys
from datetime import datetime

### wait for certain time (modulo 60 seconds)
def wait_until(nseconds):
    while True:
        currentSeconds = datetime.now().time().second
        if abs(currentSeconds - nseconds)>0:
            time.sleep(0.1)
        else:
            break
    return


def set_env():
    #################SETTING THE ENVIRONMENT#########################
    #source thisroot.sh, do startots
    print '\nPREPARING THE ENVIRONMENT \n'
    print '\nSTARTING THE OTS-DAQ \n'
    #os.system('source /home/daq/otsdaq/setup_ots.sh')
    #os.system('source /home/daq/otsdaq/build_slf7.x86_64/otsdaq/bin/StartOTS.sh')
    session = subprocess.Popen('cd /home/daq/; source ./otsdaq/setup_ots.sh; source ./otsdaq/build_slf7.x86_64/otsdaq/bin/StartOTS.sh;cd -' , shell=True)                             
    stdout, stderr = session.communicate()      
    #os.system('source /home/daq/Downloads/root/bin/thisroot.sh')
    #print '\n \n ROOT IS READY \n'

