# LLSF
LGAD laser study framework

Sensor Installation:

      1) Mount the board over the block such that it is not grounded (check resistance between 6V on the board and the block)
      2) Install the sensor, note down the channel mapping.
      3) Make sure the thermistor readings are on channel 20 of the DMM
      4) Pick one pad, find it on the oscilloscope by moving the motors, and choose the laser attenuation settings such that        you clearly see the sensor turning on and off. Note down this attenuation setting
      5) Check the photodiode signal at this attenuation setting and note down the amplitude
      6) See all the edges of the sensor to be scanned in the oscilloscope and note down the 2D position 
      7) Start the humidity logging and start the chiller
      8) Make sure the coolant from the chiller doesn't leak inside the box
      9) Now run the following labview programs on the Windows pc:

            1) Go to Documents -> LinuxLabviewShare -> LabviewDAQData. Make sure there is no data stored here, i.e., all the data should be inside the respective scan directories inside LabviewDAQData folder.
            2) Now go to LabviewDAQ folder on the destop and open Sidet_Labview VI. Run the VI by choosing sourcemeter 1 and the appropriate DMM channel. Ramp up. Make sure you see the instrument readings.
            3) Close the Kinesis motor software if it is open.
            4) Now go to Laser2DScan folder on the dektop and open the Motor2DLaserScan.vi. Put the start and end motor positions you noted earlier. Run the VI by clicking the play button. Make sure the motors home properly.
        
     10) Start the nitrogen in the box
     11) Wait for humidity to stabilize (this would take at least 4 hours)

VME:

      1) Go to /home/daq/daqSidet
      2) Run ./RunCMSTimingSidetLaser.sh

Instructions for running LLSF on Linux pc:

      1) Make sure there is enough space on the disk to save data for the whole scan --> do df -h
            If there is not enough space move data from /home/daq/Data/CMSTiming to /run/media/daq/ScanBackup/
      2) cd /home/daq/LaserScan/LLSF/2DScanScripts
      3) python Scan2D.py
      4) Check if the scan is working properly, i.e., it is changing the x-y position on the motor vi.
      5) Run the automatic dattoroot processing in another terminal window:
            cd /home/daq/LaserScan/LLSF/2DScanScripts
            python
            from AllModules import *
            RecoAll(False)
            
End of Scan:
      
      1) Note down the information diaplayed at the end of the scan in the terminal 
      2) Make an entry into the scan registry here: https://docs.google.com/spreadsheets/d/1MaJpLlSbiUbvZcat6KnmStNjslhU6v8nh6mFwZYc24g/edit#gid=0
      3) Stop the labview VIs and the humidity logging
      4) Save the humidity logs according to the scan number in the default position
      5) Move all the labview data by doing cd /home/daq/LaserScan/e/LabviewDAQData, mkdir Scan<ScanNumber>,  mv lab_meas_unsync_* Scan<ScanNumber>
      6) Do data processing by:
            cd /home/daq/LaserScan/LLSF/2DScanScripts
            python
            from AllModules import *
            process_runs(Scan number)
      7) Move all the raw and reco data /home/daq/Data/CMSTiming/Raw* into /home/daq/Data/CMSTiming/Scan<ScanNumber>/     
      8) Make 3D Triangulation plot by doing
            cd /home/daq/LaserScan/LLSF/2DScanScripts
            python
            from AllModules import *
            Plot3DMesh(scan number, amplitude cut, number of channels)
      
Stopping scan in the middle:
      
      1) source Stop2DScan script.
      2) Stop the labview program.
      3) source Stop2DScan script again.
