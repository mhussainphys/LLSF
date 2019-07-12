from AllModules import *

#SPECIFY SCAN PARAMETERS
print '#############################################################################'
print '########################### Specify Scan Parameters #########################'
print '#############################################################################'

if not debug:
    BoardName = raw_input("Board Name : ") 
    SensorName = raw_input("Sensor Name : ")
    BiasVoltage = raw_input("Bias Voltage (V) : ")
    BiasVoltage = BiasVoltage + 'V'
    LaserAttenuation = raw_input("Laser Attenuation : ")
    LaserFrequency = raw_input("Laser Frequency (kHz): ")
    LaserFrequency = LaserFrequency + 'kHz'
    AmplifierVoltage = raw_input("Amplifier Voltage (V): ")
    AmplifierVoltage = AmplifierVoltage + 'V'
    ScanStepSizeX = raw_input("Scan Step Size X (um): ")
    ScanStepSizeX = ScanStepSizeX + 'um'
    ScanStepSizeY = raw_input("Scan Step Size Y (um): ")
    ScanStepSizeY = ScanStepSizeY + 'um'
    BeamSize = raw_input("Beam Size (um): ")
    BeamSize = BeamSize + 'um'
    BoardTemperature = raw_input("Board Temperature (kOhms): ")
    BoardTemperature = BoardTemperature + 'kOhms'
else:
    BoardName = "N/A" 
    SensorName = "N/A"
    BiasVoltage = "N/A"
    LaserAttenuation = "N/A"
    LaserFrequency = "N/A"
    AmplifierVoltage = "N/A"
    ScanStepSizeX = "N/A"
    ScanStepSizeY = "N/A"
    BeamSize = "N/A"
    BoardTemperature = "N/A"

print '\n#############################################################################'
print '\n\n########################### Setting Scan Environment #########################'
set_env()

print '\nTelling motor to start the scan and go to initial position'
ScanInitiateHandle = open(ScanInitiateFile, "w")
ScanInitiateHandle.write("1")
ScanInitiateHandle.close()

print '\n############################ Initializing the OTS-DAQ #######################'
if not debug: init_ots()
print '\n############################ Configuring the OTS-DAQ #######################'
if not debug: config_ots()
print '\nSleeping for 30 seconds to give time to VME to configure'
if sleepMargin: time.sleep(30) # Give time to VME for configuring and motor to move to initial position

print '\nReading the next scan number'
ScanNumber = scan_num() 
print 'Next scan number : ', ScanNumber
ScanNumberWriteHandle = open(ScanNumberFile, "w")
ScanNumberWriteHandle.write(str(ScanNumber + 1))
ScanNumberWriteHandle.close()

print '\nFetching the starting run number for the scan' 
RunNumber = get_run_number() #Finding the max run number in the run registry
StartRunNumber = RunNumber


#************************************************************************************************************************
#************************************************************************************************************************
#************************************************************************************************************************
#************************************************************************************************************************

print '\n#############################################################################'
print '######################## Starting 2D scan of the sensor #######################'
print '#############################################################################\n'

##### Waiting for motor to get to the initial position #####
wait_for_file(MotorReadyToMoveFile, 0,'Waiting for motor to get to the initial 2D position')    

##### Starting scan paramters #####
InitialMotorPositionY, InitialMotorPositionX = motor_pos()
ScanStartTime = datetime.now()


ScanStatus = WriteStatusFile()

while not StopScan:

    LastIterationBool = wait_for_file(MotorReadyToMoveFile, 0,'Waiting for motor to get to the next position')
    if LastIterationBool:
        StopScan = True
        print '\n################## Last run of the scan ###############\n'

    if sleepMargin: time.sleep(TimeToWaitForMotor) #wait for some time to give motor time to move (like 1s). Because still not sure if the motor has completed the move. Can't find any method for this.

    print '############################'
    CurrentMotorPositionY, CurrentMotorPositionX = motor_pos()
    print '\n\nCurrent 2D motor position (x,y) : (%f,%f)' % (CurrentMotorPositionX, CurrentMotorPositionY) #Motor is not guaranteed to have moved
    
    print 'Run Number: %d \n' % RunNumber
    if run_registry_exists(RunNumber): 
        print "ERROR: this run number already exists. Exiting!"
        break   

    XMotorPositionList.append(CurrentMotorPositionX)
    YMotorPositionList.append(CurrentMotorPositionY)
    RunNumberList.append(RunNumber)

    if not debug: start_ots(RunNumber) #start ots-daq (2.5s runs)
    MeasTimestamp = (datetime.now() - datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")).total_seconds() - 3600
    TimestampList.append(MeasTimestamp)
    if not debug: stop_ots()  #stop otsdaq (0.8 second delay after stop)

    MotorReadyToMoveHandle = open(MotorReadyToMoveFile, "w")
    MotorReadyToMoveHandle.write("1")
    MotorReadyToMoveHandle.close()
    
    # Write scan file in the middle of the scan
    MeasTemp, MeasVoltage, MeasCurrent = ConvertEnv(MeasTimestamp)
    ParameterList = [RunNumber, MeasTimestamp, CurrentMotorPositionX, CurrentMotorPositionY, MeasVoltage, MeasCurrent, MeasTemp, BoardName, SensorName, ScanStepSizeY, ScanStepSizeX, AmplifierVoltage, LaserAttenuation, LaserFrequency, BeamSize]
    WriteLaserScanDataFile(ScanNumber, ParameterList)

    RunNumber = RunNumber + 1
    tmpStatusFile, ScanStatus = ReadStatusFile()
    if not ScanStatus:
        StopScan = True     

CloseFile(tmpStatusFile)

#************************************************************************************************************************
#************************************************************************************************************************
#************************************************************************************************************************
#************************************************************************************************************************

if WriteEndScanFiles:
    print '\n\n######################## Writing Run and Scan files for the scan ##############################\n\n'
    for i in range(0, RunNumber - StartRunNumber):
       if run_exists(RunNumberList[i]):
          Temp20,Voltage1,Current1 = ConvertEnv(TimestampList[i])
          RunFileParametersList = [RunNumberList[i], ScanNumber, XMotorPositionList[i], YMotorPositionList[i], BoardName, SensorName, BiasVoltage, ScanStepSizeY, ScanStepSizeX, AmplifierVoltage, LaserAttenuation, LaserFrequency, BeamSize, BoardTemperature, Temp20,Voltage1,Current1]      
          WriteFile(RunFileParametersList, "run")
       else:
          print "Run %i failed." % RunNumberList[i]

    ScanFileParametersList = [ScanNumber, StartRunNumber, RunNumber - 1, InitialMotorPositionY, CurrentMotorPositionY, InitialMotorPositionX, CurrentMotorPositionX, BoardName, BiasVoltage, ScanStepSizeY, ScanStepSizeX, AmplifierVoltage, LaserAttenuation, LaserFrequency, BeamSize, BoardTemperature]
    WriteFile(ScanFileParametersList, "scan")

print '\n#############################################################################'
print '################################ 2D scan complete #############################'
print '#############################################################################\n'

ScanStopTime = datetime.now()
ScanDuration = (ScanStopTime - ScanStartTime).total_seconds()

print '########################## Printing scan parameters ##########################\n'
print 'Scan number : ', ScanNumber
print 'Scan start time : ', ScanStartTime
print 'Scan stop time : ', ScanStopTime
print 'Scan time elapsed (hours) : ', ScanDuration/3600
print 'Start run number : ', StartRunNumber
print 'Stop run number : ', RunNumber - 1
print 'Total runs taken : ',  RunNumber - StartRunNumber 

print '########################## Moving labview data within the mounted folder ##########################\n'
os.system('mkdir %sScan%d/' % (LabviewDAQDataDir, ScanNumber))
os.system('mv %slab_meas_unsync* %sScan%d' % (LabviewDAQDataDir, LabviewDAQDataDir, ScanNumber))