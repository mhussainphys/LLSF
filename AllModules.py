import time
from datetime import datetime
import numpy as np
from numpy import loadtxt
import getpass
import os
import subprocess as sp
import socket
import sys
import glob

ip_address = "192.168.133.50"
LaserScanDir = "/home/daq/LaserScan/"
MotorControlMount = "%sLaserScanWindows/" % LaserScanDir
LabviewDAQMount = "%se/" % LaserScanDir

MotorControlFilesDir = "%sMotorControlTextFiles/" % MotorControlMount
LabviewDAQDataDir = "%sLabviewDAQData/" % LabviewDAQMount
Motor2DPositionFile = "%sMotor2DPosition.txt" % MotorControlFilesDir
LastIterationBoolFile = "%sLastIterationBool.txt" % MotorControlFilesDir
MotorReadyToMoveFile = "%sMotorReadyToMove.txt" % MotorControlFilesDir
ScanInitiateFile = "%sScanInitiate.txt" % MotorControlFilesDir
ScanNumberFile = "%sScanRegistry/scan_number.txt" % LaserScanDir
runRegistryDir = "%sRunRegistry/" % LaserScanDir
scanRegistryDir = "%sScanRegistry/" % LaserScanDir
vmeRawDataDir = "/home/daq/Data/CMSTiming/"
scopeRawDataDir = "/home/daq/Data/NetScopeTiming/"
runFileName = "/home/daq/otsdaq/srcs/otsdaq_cmstiming/Data_2018_09_September/ServiceData/RunNumber/OtherRuns0NextRunNumber.txt"

TimeToWaitForMotor = 5
debug = False
if debug:
	sleepMargin = False 
else:
	sleepMargin = True
ScanStartTime = []
XMotorPositionList = []
YMotorPositionList = []
RunNumberList = []
LastIteration = False 
StopScan = False

def set_env():
    print '\nPREPARING THE ENVIRONMENT \n'
    print '\nSTARTING THE OTS-DAQ \n'
    session = subprocess.Popen('cd /home/daq/; source ./otsdaq/setup_ots.sh; source ./otsdaq/build_slf7.x86_64/otsdaq/bin/StartOTS.sh;cd -' , shell=True)                             
    stdout, stderr = session.communicate()

def wait_for_file(filename, l, message=""):
 status_file = open(filename, "r")
 counter = 0
 while status_file.read() != str(l):
   status_file.close()
   time.sleep(1)
   status_file = open(filename, "r")
   if message !="" and counter % 10 == 0 : print message
   counter = counter + 1
 LastIterationBoolHandle = open(LastIterationBoolFile, "r")
 if LastIterationBoolHandle.read() == str(1):
 	LastIterationBool = True
 else:
 	LastIterationBool = False
 status_file.close()
 return LastIterationBool 

def motor_pos():
 motor_pos = open(Motor2DPositionFile, "r")
 Yposition = float(motor_pos.read().split("\t")[0])
 motor_pos.close()
 motor_pos = open(Motor2DPositionFile, "r")
 XPosition = float(motor_pos.read().split("\t")[1])
 motor_pos.close() 
 return Yposition, XPosition

def scan_num():
 scan_number = open(ScanNumberFile, "r")
 scan  = int(scan_number.read())
 scan_number.close()
 return scan


def init_ots():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = "OtherRuns0,Initialize"
    sock.sendto(MESSAGE, (ip_address, 8000))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Initialize: received message:", data
    time.sleep(5)

def config_ots():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = "OtherRuns0,Configure,FQNETConfig"
    sock.sendto(MESSAGE, (ip_address, 8000))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Configure: received message:", data
    time.sleep(5)

def start_ots(run_number,Delay=True):
    runFile = open(runFileName)
    nextRun = int(runFile.read().strip())
    runFile.close()

    incrementRunFile = open(runFileName,"w")
#    print str(nextRun+1)+"\n"                                                                                                                    
    incrementRunFile.write(str(nextRun+1)+"\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = "OtherRuns0,Start, %d" % (nextRun) 
    sock.sendto(MESSAGE, (ip_address, 8000))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Start: received message:", data
    if Delay: time.sleep(4)

def stop_ots(Delay=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = "OtherRuns0,Stop"
    sock.sendto(MESSAGE, (ip_address, 8000))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Stop: received message:", data
    if Delay: time.sleep(1)

def run_registry_exists(run_number):
    rawPath = "%srun%i.txt" % (runRegistryDir, run_number)
    return os.path.exists(rawPath)

def run_exists(run_number):
    vors = 'vme'
    if vors == 'vme':
        rawPath = "%s/RawDataSaver0CMSVMETiming_Run%i_0_Raw.dat" % (vmeRawDataDir, run_number)
    if vors == 'scope':
        rawPath = "%s/RawDataSaver0NetScopeTiming_Run%i_0_Raw.dat" % (scopeRawDataDir, run_number)        
    return os.path.exists(rawPath)

def WriteFile(ParameterList, FileName):
	if FileName == "scan":	
		FileHandle = open("%sscan%d.txt" % (scanRegistryDir,ParameterList[0]), "a+") 
	elif FileName == "run":
		FileHandle = open("%srun%d.txt" % (runRegistryDir,ParameterList[0]), "a+")
	else:
		print "Wrong File Name"
	for parameter in ParameterList:
		FileHandle.write(str(parameter) + "\n")
	FileHandle.close()

def get_run_number(): #include otsdaq run number also
    #otsmax = max([int(x.split("%srun" % runRegistryDir)[1].split(".txt")[0]) for x in glob.glob("%srun*" % runRegistryDir)])
    next_run_number = open(runFileName, "r")
    run_number = int(next_run_number.read())
    #run_number = otsmax
    return run_number

def Resistance_calc(T): #Function to calculate resistance for any temperature
    R0 = 100 #Resistance in ohms at 0 degree celsius
    alpha = 0.00385 
    Delta = 1.4999 #For pure platinum
    if T < 0:
        Beta = 0.10863
    elif T > 0:
        Beta = 0
    RT = (R0 + R0*alpha*(T - Delta*(T/100 - 1)*(T/100) - Beta*(T/100 - 1)*((T/100)**3)))*100
    return RT

def Temp_calc(R): #Function to calculate temperature for any resistance
    Temp_x = np.linspace(-30, 30, num=100) #Points to be used for interpolation        
    Resis_y = np.array([])
    for i in range(len(Temp_x)):
        Resis_y = np.append(Resis_y,Resistance_calc(Temp_x[i]))
    Temperature_R = np.interp(R, Resis_y, Temp_x)
    #plt.plot(Temp_x, Resis_y, 'o')
    #plt.show()
    return Temperature_R

def PlotEnv(ScanNumber):
        labview_unsync_base_path = '%sScan%d/' % (LabviewDAQDataDir, ScanNumber)
        labview_file_list = sorted([float(x.split("lab_meas_unsync_")[-1].split(".txt")[0]) for x in glob.glob(labview_unsync_base_path + "/lab_meas_unsync_*")])
        ScanStartTime = labview_file_list[0].split("lab_meas_unsync_")[1]       
        all_labview_array = np.array([])
        for i in range(len(labview_file_list)):
            labview_file_name = labview_unsync_base_path + "/lab_meas_unsync_%.3f.txt" % labview_file_list[i]
            labview_array = np.array(np.loadtxt(labview_file_name, delimiter='\t', unpack=False))
            if i == 0:
                all_labview_array = labview_array            
            else: 
                all_labview_array = np.vstack((all_labview_array, labview_array))
        
        Temp = np.array([])
        itera = 0 
        for row in all_labview_array:
            Temp = np.append(Temp,Temp_calc(all_labview_array[itera,21]))
            itera = itera + 1

        plt.subplot(1, 3, 1)
        plt.plot((all_labview_array[:,0] - ScanStartTime), all_labview_array[:,2]*-1000000, '.') #0 time, 1 sm1v, 2 sm1i, 3 sm2v, 4 sm2i....and 8 before so on
        #plt.axis([0, 12, 0, -50])
        plt.ylabel(u"Current (\u03bcA)")
        plt.xlabel('Time (s)')
        plt.grid(True)


        plt.subplot(1, 3, 2)
        plt.plot((all_labview_array[:,0] - ScanStartTime), all_labview_array[:,1]*-1, '.') #0 time, 1 sm1v, 2 sm1i, 3 sm2v, 4 sm2i....and 7 before so on
        #plt.axis([0, 12, 0, -400])
        plt.ylabel(u"Voltage (V)")
        plt.xlabel('Time (s)')
        plt.grid(True)


        plt.subplot(1, 3, 3)
        plt.plot(all_labview_array[:,0] - ScanStartTime, Temp[:], '.') #0 time, 1 sm1v, 2 sm1i, 3 sm2v, 4 sm2i....and so on
        plt.axis([0, 12, 0, 30])
        plt.ylabel(u'Temperature (\u00B0C)')
        plt.xlabel('Time (s)')
        plt.grid(True)
        plt.show()