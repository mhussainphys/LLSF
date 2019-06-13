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
from other_func import set_env
from labview_tools import wait_for_file, motor_pos, run_num, scan_num
from TCP_com import init_ots, config_ots, start_ots, stop_ots #in-built 5s delay in all of them
from database_util import run_registry_exists, run_exists,write_runfile, append_scanfile, write_scanfile, process_runs, analysis_plot, get_run_number, append_scanfile, dattoroot

debug = False
sleepMargin = True 

#USING VME OR SCOPE
vors = raw_input("\nVME (type vme) OR SCOPE (type scope)?\n") 
if vors == 'vme':
   isvme = 1
elif vors == 'scope':
   isvme = 0

scan_in = raw_input("\nSCAN IN (options: 'x', 'y', 't'): \n")

#SPECIFY SCAN PARAMETERS
print '\n\n\n#####################SPECIFY SCAN PARAMETERS###################\n\n\n'
print 'Write everything with proper signs and without space. Type "NA" if you dont want to include the field in the name\n' 
board_sn = raw_input("Which board are you using?") 
bias_volt = raw_input("BIAS VOLTAGE (V) : ")
bias_volt = bias_volt + 'V'
laser_amp = raw_input("LASER AMPLITUDE : ")
laser_fre = raw_input("LASER FREQUENCY (kHz): ")
laser_fre = laser_fre + 'kHz'
amp_volt = raw_input("AMPLIFIER VOLTAGE (V): ")
amp_volt = amp_volt + 'V'
scan_stepsize = raw_input("SCAN STEP SIZE (mm): ")
scan_stepsize = scan_stepsize + 'mm'
beam_spotsize = raw_input("BEAM SPOT SIZE (um): ")
beam_spotsize = beam_spotsize + 'um'
temp = raw_input("TEMPERATURE_RES (kOhms): ")
temp = temp + 'kOhms'

#SETTING ENVIRONMENT
set_env()

#TELLING MOTOR WHICH SCAN TO DO
xory_handle = open("/home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/xory.txt", "w")
xory_handle.write(scan_in)
xory_handle.close()


#CONFIGURING AND INITIALIZING THE OTSDAQ
print 'INTITIALIZING THE OTS-DAQ'
if not debug: init_ots()
print 'CONFIGURING THE OTS-DAQ'
if not debug: config_ots()
time.sleep(30) #remove this later

scan_number = scan_num() #Reading scan number
print 'Scan number: ', scan_number
#run_number = run_num() + 1 #Reading run number (increment from where we left off) 

#Increment scan number in the text file
scan_write = open("/home/daq/LaserScan/ScanRegistry/scan_number.txt", "w")
scan_write.write(str(scan_number + 1))
scan_write.close()

#Run Number 
run_number = get_run_number() #Finding the max run number in the run registry
start_run_number = run_number

run_number_list = []
motor_pos_list = []

#SCAN IF LOOP
if scan_in == 'x' or scan_in == 'y':
        print '\n\n############################STARTING POSITION SCAN###############################\n\n'
        wait_for_file("/home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/motor_con.txt", 0,'Waiting for motor to get to initial position')    
        motor_pos_init = motor_pos()

        scan_start_time = datetime.now()
        i = 0 
        while i != 2:   
            wait_for_file("/home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/motor_con.txt", 0,'Waiting for motor to get to the next position')
            if sleepMargin: time.sleep(3) #wait for some time to give motor time to move (like 1s). Because still not sure if the motor has completed the move. Can't find any method for this.

            print '############################'
            print '\n\nMotor position : ', motor_pos() #Motor is not guaranteed to have moved
            motor_pos_list.append(motor_pos())

            #time.sleep(10)
            print 'Run Number: %d \n' % run_number
            if run_registry_exists(run_number): 
                print "ERROR: this run number already exists. Exiting!"
                break
            run_number_list.append(run_number)

            if not debug: start_ots(run_number) #start ots-daq
            #time.sleep(1)
            if not debug: stop_ots()  #stop otsdaq
            #time.sleep(10)
            motorcon_handle = open("/home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/motor_con.txt", "w")
            motorcon_handle.write("1")
            motorcon_handle.close()

            
            
            #For the end run of the OTS-DAQ 
            lastiter_handle = open("/home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/last_iter.txt", "r")
            i = int(lastiter_handle.read()) + 1
            if i == 2:

                 print '##################################'
                 print '\nRUNNING OTSDAQ FOR THE LAST TIME \n'


                 #wait_for_file("/home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/motor_con.txt", 0,'Waiting for motor to get to the next position')
                 if sleepMargin: time.sleep(5) 

                 print '\nMotor moved to : ', motor_pos()
                 motor_pos_list.append(motor_pos())
                 run_number = run_number + 1
                 time.sleep(10)
                 print 'Run Number: %d \n' % run_number
                 run_number_list.append(run_number)
                 
                 if not debug: start_ots(run_number) #start ots-daq
                 #time.sleep(1)
                 if not debug: stop_ots()  #stop otsdaq                 

            lastiter_handle.close()

            run_number = run_number + 1            

elif scan_in == 't':
            print '\n\n############################STARTING TIME SCAN###########################\n\n'
            tot_time = raw_input("Give the scan time duration (in hrs).")
            motor_pos = raw_input("Enter the motor position.")            
            stop_scan = int(float(tot_time) * 3600/75) #should be 210
            scan_counter = 0
            while scan_counter != stop_scan:       
                time.sleep(25)
                scan_counter = scan_counter + 1
                start_ots(run_number) #start ots-daq
                #Writing run files
                write_runfile(float(motor_pos), run_number, scan_number, vors, board_sn, bias_volt, laser_amp, laser_fre, amp_volt, scan_in, scan_stepsize, beam_spotsize, temp)
                #Written run files                
                time.sleep(10)
                stop_ots()  #stop otsdaq
                time.sleep(10) #should be 170
                run_number = run_number + 1
            #Writing scan file    
            write_scanfile(start_run_number, run_number - 1, scan_number, motor_pos, motor_pos, vors, board_sn, bias_volt, laser_amp, laser_fre, amp_volt, scan_in, scan_stepsize, beam_spotsize, temp)



print '\n\n######################################SCAN COMPLETE#######################################\n\n'

scan_stop_time = datetime.now()
scan_time_elapsed = (scan_stop_time - scan_start_time).total_seconds()

################################### SCAN STATUS ####################################
print 'Scan start time: ', scan_start_time
print 'Scan stop time: ', scan_stop_time
print 'Scan time elapsed: ', scan_time_elapsed/3600
print 'Start run number: ', start_run_number
print 'Stop run number: ', run_number - 1
print 'Total runs taken: ',  run_number - start_run_number 


print '\n\n######################## Writing Run and Scan files for the scan ##############################\n\n'
for i in range(0, run_number - start_run_number):
   if run_exists(run_number_list[i],vors):
      write_runfile(motor_pos_list[i], run_number_list[i], scan_number, vors, board_sn, bias_volt, laser_amp, laser_fre, amp_volt, scan_in, scan_stepsize, beam_spotsize, temp)
   else:
      print "Run %i failed." % run_number_list[i]

write_scanfile(start_run_number, run_number - 1, scan_number, motor_pos_init, motor_pos(), vors, board_sn, bias_volt, laser_amp, laser_fre, amp_volt, scan_in, scan_stepsize, beam_spotsize, temp)






#DATTOROOT
#dattoroot(scan_number)

#PROCESS RUNS
#process_runs(scan_number)

#PLOT DATA
#analysis_plot(scan_number)


