import time
from datetime import datetime
import numpy as np
from numpy import loadtxt
import getpass
import os
import subprocess 
import socket
import sys
import glob
from GetEnvFunc import *

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
AnalysisVMEDir = "%sAnalysisVME/" % LaserScanDir
vmeRawDataDir = "/home/daq/Data/CMSTiming/"
scopeRawDataDir = "/home/daq/Data/NetScopeTiming/"
runFileName = "/home/daq/otsdaq/srcs/otsdaq_cmstiming/Data_2018_09_September/ServiceData/RunNumber/OtherRuns0NextRunNumber.txt"
LaserScanDataFileName = '%sLaserScanDataRegistry/' % LaserScanDir

TimeToWaitForMotor = 5
debug = False
if debug:
	sleepMargin = False 
else:
	sleepMargin = True
ScanStartTime = []
XMotorPositionList = []
YMotorPositionList = []
TimestampList = []
RunNumberList = []
LastIteration = False 
StopScan = False
WriteEndScanFiles = True

def WriteLaserScanDataFile(ScanNumber, ParameterList):
    ScanDataFileHandle = open(LaserScanDataFileName + 'scan' + str(ScanNumber) + '.txt' ,"a+")
    for parameter in ParameterList:
        ScanDataFileHandle.write(str(parameter) + "\t") #dumb way to do it, the clever way is not working : somehow list.index() doesn't work for more than 5 element list
    ScanDataFileHandle.write("\n")
    ScanDataFileHandle.close()

def WriteStatusFile():
    # Use Status file to tell 2DScan when to stop.
    if os.path.exists("Scan.status"):
        os.remove("Scan.status")
    statusFile = open("Scan.status","w") 
    statusFile.write("START") 
    statusFile.close() 
    return True

def ReadStatusFile():
    #################################################
    #Check for Stop signal in Scan.status file
    #################################################
    tmpStatusFile = open("Scan.status","r") 
    tmpString = (tmpStatusFile.read().split())[0]
    ScanStatus = True
    if (tmpString == "STOP" or tmpString == "stop"):
        print "Detected stop signal.\nStopping 2DScan ...\n\n"
        ScanStatus = False    
    return tmpStatusFile, ScanStatus

def CloseFile(tmpStatusFile):
    tmpStatusFile.close()

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
    if Delay: time.sleep(2.5)

def stop_ots(Delay=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = "OtherRuns0,Stop"
    sock.sendto(MESSAGE, (ip_address, 8000))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Stop: received message:", data
    if Delay: time.sleep(0.8)

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
        import matplotlib.pyplot as plt
        labview_unsync_base_path = '%sScan%d/' % (LabviewDAQDataDir, ScanNumber)
        labview_file_list = sorted([float(x.split("lab_meas_unsync_")[-1].split(".txt")[0]) for x in glob.glob(labview_unsync_base_path + "/lab_meas_unsync_*")])
        ScanStartTime = labview_file_list[0]       
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
            Temp = np.append(Temp,Temp_calc(all_labview_array[itera,23])) #23 for channel 20 in labview program
            itera = itera + 1
        
            print itera

        plt.subplot(1, 3, 1)
        plt.plot((all_labview_array[:,0] - ScanStartTime), all_labview_array[:,2]*(-1000000), '.') #0 time, 1 sm1v, 2 sm1i, 3 sm2v, 4 sm2i....and 8 before so on
        #plt.axis([0, 12, 0, -50])
        plt.ylabel(u"Current (\u03bcA)")
        plt.xlabel('Time (s)')
        plt.grid(True)


        plt.subplot(1, 3, 2)
        plt.plot((all_labview_array[:,0] - ScanStartTime), all_labview_array[:,1]*-1 - 1.1 * all_labview_array[:,2]*(-1000000) , '.') #0 time, 1 sm1v, 2 sm1i, 3 sm2v, 4 sm2i....and 7 before so on
        #plt.axis([0, 12, 0, -400])
        plt.ylabel(u"LGAD Voltage (V)")
        plt.xlabel('Time (s)')
        plt.grid(True)


        plt.subplot(1, 3, 3)
        plt.plot(all_labview_array[:,0] - ScanStartTime, Temp[:], '.') #0 time, 1 sm1v, 2 sm1i, 3 sm2v, 4 sm2i....and so on
        #plt.axis([0, 12, 0, 30])
        plt.ylabel(u'Temperature (\u00B0C)')
        plt.xlabel('Time (s)')
        plt.grid(True)
        plt.show()

def process_runs(ScanNumber):
    print '############################PROCESSING RUNS#############################'
    #Calling a script to combine the trees and make text files for plotting.
    ScanLines = [line.rstrip('\n') for line in open("%sscan%d.txt"  % (scanRegistryDir,ScanNumber))]
    scan_number = ScanLines[0]
    StartRunNumber = ScanLines[1]
    StopRunNumber = ScanLines[2]
    print 'Start run number: ', int(StartRunNumber)
    print 'Stop run number: ', int(StopRunNumber)
    n_processed = 0
    vors = 'vme'
    for i in range (int(StartRunNumber), int(StopRunNumber) + 1): 
        print 'Processing run number: ', i    
        if run_exists(i) and run_registry_exists(i):       
            run_lines = [line.rstrip('\n') for line in open("%srun%d.txt"  % (runRegistryDir,i))]
            motor_pos_x = run_lines[2]
            motor_pos_y = run_lines[3]
            print 'X Motor position: ', float(motor_pos_x)
            print 'Y Motor position: ', float(motor_pos_y)
            combineCmd = ''' root -l -q 'combine.c("%s",%d,%f,%f)' ''' % (str(i),int(scan_number), float(motor_pos_x), float(motor_pos_y))
            os.system(combineCmd)
            n_processed = n_processed + 1
    print 'Processed %i out of expected %i runs attempted in scan.' %(n_processed , int(StopRunNumber)-int(StartRunNumber)+1)

def Plot3D(ScanNumber, AmplitudeCut, NumberOfChannels):
    from matplotlib import pyplot
    from mpl_toolkits.mplot3d import Axes3D
    fig = pyplot.figure()
    ax = Axes3D(fig)
    LaserScanArray = np.loadtxt('%sprocessdata_%d.txt' % (AnalysisVMEDir, ScanNumber), delimiter=' ', unpack=False)

    for channel in range (1, NumberOfChannels + 1):
        if channel != 9:
            x = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),0].tolist()
            y = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),1].tolist()
            z = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),channel + 2].tolist()
            if channel  % 2 == 0:
                color = 'r'
            else:
                color = 'k'
            ax.scatter(x, y, z, label='', c=color)
    
    axis_font = {'fontname':'Arial', 'size':'15'}
    ax.set_xlabel("X Position [mm]",**axis_font)
    ax.set_ylabel("Y Position [mm]",**axis_font)
    ax.set_zlabel("Amplitude [mV]",**axis_font)
    #ax.set_zbound(upper=30,lower=0)
    #ax.set_ybound(upper=49,lower=65)
    #ax.set_xbound(upper=7,lower=12)
    ax.legend()
    SaveFigure = raw_input("Do you want to save the output figure (y/n) ?: ")
    if SaveFigure == 'y': pyplot.savefig('%sscan3D_%s.png' %(AnalysisVMEDir, ScanNumber))
    pyplot.show()

def Plot3DMesh(ScanNumber, AmplitudeCut, NumberOfChannels):
    
    from matplotlib import pyplot
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.tri as mtri

    LaserScanArray = np.loadtxt('%sprocessdata_%d.txt' % (AnalysisVMEDir, ScanNumber), delimiter=' ', unpack=False)
    
    XPosition = np.array([])
    YPosition = np.array([])
    Amplitude = np.array([])
    
    for channel in range (1, NumberOfChannels + 1):
                
        if channel == 13 or channel == 16: 
            for row in LaserScanArray: 
                if row[channel + 2] < 19 and row[channel + 2] > 10:
                    row[channel + 2] =  row[3]

        if channel == 1:
            
            XPosition = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),0]
            YPosition = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),1]
            Amplitude = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),channel + 2]

        elif channel != 9:

            x = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),0]
            y = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),1]
            z = LaserScanArray[np.logical_not(LaserScanArray[:,channel + 2]<AmplitudeCut),channel + 2]
            
            XPosition = np.concatenate((XPosition, x)) 
            YPosition = np.concatenate((YPosition, y))
            Amplitude = np.concatenate((Amplitude, z))  

    
    triang = mtri.Triangulation(XPosition, YPosition)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')

    ax.plot_trisurf(XPosition,YPosition,Amplitude, cmap='jet')
    ax.scatter(XPosition,YPosition,Amplitude, marker='.', s=20, c="black", alpha=0.5)
    ax.view_init(elev=60, azim=-45)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Amplitude')
    #ax.set_zbound(upper=30,lower=0)
    ax.set_ybound(upper=22,lower=8)
    ax.set_xbound(upper=25,lower=8)
    plt.show()
    #pyplot.show()

def dattoroot(scan_number):
    print '############################CONVERTING TO ROOT FILES#############################'
    scan_lines = [line.rstrip('\n') for line in open("%sscan%d.txt"  % (scanRegistryDir,scan_number))]
    start_run_number = scan_lines[1]
    stop_run_number = scan_lines[2]
    vors = 'vme'

    print 'Start run number: ', int(start_run_number)
    print 'Stop run number: ', int(stop_run_number)
    n_processed = 0
    for i in range (int(start_run_number), int(stop_run_number) + 1):
        print 'DatToRoot for run number: ', i   
        if run_exists(i) and run_registry_exists(i):
            if vors == 'vme':
                isvme = 1
                dattorootCmd = ". /home/daq/TimingDAQ/dattoroot.sh /home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run%i_0_Raw.dat /home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run%i_0_Raw.root" % ( i, i)        
            elif vors == 'scope':
                isvme = 0
                dattorootCmd = ". /home/daq/TimingDAQ/dattorootscope.sh /home/daq/Data/NetScopeTiming/RawDataSaver0NetScope_Run%i_0_Raw.dat /home/daq/Data/NetScopeTiming/RawDataSaver0NetScope_Run%i_0_Raw.root" %(i, i)       
            os.system(dattorootCmd)
            n_processed = n_processed + 1
    print 'Converted %i out of expected %i runs attempted in scan.' % (n_processed , int(stop_run_number)-int(start_run_number)+1)

def RecoAll(DoItOnce):

    while not DoItOnce:

        ListRawFiles = [(x.split('CMSVMETiming_Run')[1].split(".dat")[0].split("_")[0]) for x in glob.glob('%s*' % '/home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run')]
        #ListRecoFiles = [(x.split('CMSVMETiming_Run')[1].split(".root")[0].split("_")[0]) for x in glob.glob('%s*' % '/home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run')]
        SetRawFiles = set([int(x) for x in ListRawFiles])
        #SetRecoFiles = set([int(x) for x in ListRecoFiles])
        #SetToProcess = SetRecoFiles - SetRawFiles
        #print Lis
        
        #print SetRecoFiles
        #print SetRawFiles
        #if len(SetToProcess) == 0:
        #    print 'No runs to process.' 
        #else:
        for run in SetRawFiles:
            RecoPath = '/home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run%i_0_Raw.root' % run
            RawPath = 'RawDataSaver0CMSVMETiming_Run%i_0_Raw.dat' % run
            if not os.path.exists(RecoPath) and not os.popen('lsof -f -- /home/daq/Data/CMSTiming/%s |grep -Eoi %s' % (RawPath, RawPath)).read().strip() == RawPath:
                print 'Processing run ', run
                dattorootCmd = ". /home/daq/TimingDAQ/dattoroot.sh /home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run%i_0_Raw.dat /home/daq/Data/CMSTiming/RawDataSaver0CMSVMETiming_Run%i_0_Raw.root" % (run, run)
                os.system(dattorootCmd)
            else:
                print 'Run %i already processed' % run
        time.sleep(2)