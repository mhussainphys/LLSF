import time
import numpy as np
from numpy import loadtxt
import getpass
import os
import subprocess as sp
import socket
import sys
import glob
from bisect import bisect_left

labview_unsync_base_path = '/home/daq/LaserScan/e/LabviewDAQData/'

def greatest_number_less_than_value(seq,value):
	if bisect_left(seq,value)>0:
		return seq[bisect_left(seq,value)-1]
	else: return seq[0]

def GetEnvMeas(timestamp):
																																																								
	LabviewFlag = False
	all_labview_array = np.array([])    

	labview_file_list = sorted([float(x.split("lab_meas_unsync_")[-1].split(".txt")[0]) for x in glob.glob(labview_unsync_base_path + "/lab_meas_unsync_*")])
	exact_labview_file = greatest_number_less_than_value(labview_file_list, timestamp)
	index_labview_file = labview_file_list.index(exact_labview_file)
	labview_file_name = labview_unsync_base_path + "/lab_meas_unsync_%.3f.txt" % labview_file_list[index_labview_file]
	all_labview_array = np.array(np.loadtxt(labview_file_name, delimiter='\t', unpack=False))

	if all_labview_array.size == 0:
		index_labview_file = index_labview_file - 1
		labview_file_name = labview_unsync_base_path + "/lab_meas_unsync_%.3f.txt" % labview_file_list[index_labview_file]
		all_labview_array = np.array(np.loadtxt(labview_file_name, delimiter='\t', unpack=False))

	if all_labview_array.size != 0:
	
		if len(all_labview_array.shape) == 1:
			all_labview_array_time_list = all_labview_array[0]
		else:
			all_labview_array_time_list = all_labview_array[:,0].tolist()
																																													
		synced_array = np.array([])
		if (not isinstance(all_labview_array_time_list,list)):
			labview_time = all_labview_array_time_list
			delta_time = labview_time - timestamp
			if abs(delta_time) > 100:
				LabviewFlag = True
			else:
				#Resis13 = all_labview_array[1]
				#Resis14 = all_labview_array[2]
				#Resis15 = all_labview_array[3]
				#Resis16 = all_labview_array[4]
				#Resis17 = all_labview_array[5]
				#Resis18 = all_labview_array[6]
				#Resis19 = all_labview_array[7]
				Resis20 = all_labview_array[23]
				Voltage1 = all_labview_array[1]
				Current1 = all_labview_array[2]
				#Voltage2 = all_labview_array[11]
				#Current2 = all_labview_array[12]
				#Voltage3 = all_labview_array[13]
				#Current3 = all_labview_array[14]
		else:
			labview_time = min(all_labview_array_time_list, key=lambda x:abs(x-float(timestamp)))
			delta_time = labview_time - timestamp
			if abs(delta_time) > 100:
				LabviewFlag = True
			else:
				index_labview_time = all_labview_array_time_list.index(float(labview_time))
				#Resis13 = all_labview_array[index_labview_time,1]
				#Resis14 = all_labview_array[index_labview_time,2]
				#Resis15 = all_labview_array[index_labview_time, 3]
				#Resis16 = all_labview_array[index_labview_time, 4]
				#Resis17 = all_labview_array[index_labview_time, 5]
				#Resis18 = all_labview_array[index_labview_time, 6]
				#Resis19 = all_labview_array[index_labview_time, 7]
				Resis20 = all_labview_array[index_labview_time, 23]
				Voltage1 = all_labview_array[index_labview_time, 1]
				Current1 = all_labview_array[index_labview_time, 2]
				# Voltage2 = all_labview_array[index_labview_time, 11]
				# Current2 = all_labview_array[index_labview_time, 12]
				# Voltage3 = all_labview_array[index_labview_time, 13]
				# Current3 = all_labview_array[index_labview_time, 14]
		
		if LabviewFlag:
			# Resis13 = -1
			# Resis14 = -1
			# Resis15 = -1
			# Resis16 = -1
			# Resis17 = -1
			# Resis18 = -1
			# Resis19 = -1
			Resis20 = -1
			Voltage1 = -1
			Current1 = -1
			# Voltage2 = -1
			# Current2 = -1
			# Voltage3 = -1
			# Current3 = -1

	else:
			# Resis13 = -1
			# Resis14 = -1
			# Resis15 = -1
			# Resis16 = -1
			# Resis17 = -1
			# Resis18 = -1
			# Resis19 = -1
			Resis20 = -1
			Voltage1 = -1
			Current1 = -1
			# Voltage2 = -1
			# Current2 = -1
			# Voltage3 = -1
			# Current3 = -1

	return Resis20, Voltage1, Current1

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


def Temp_calc_NTC(R): #Function to calculate temperature for any resistance                                                                                                                                                                       
	Temp_x = np.linspace(-30, 30, num=61) #Points to be used for interpolation                                                                                                                                                               
	Resis_y = np.array([88500,83200,78250,73600,69250,65200,61450,57900,54550,51450,48560,45830,43270,40860,38610,36490,34500,32630,30880,29230,27670,26210,24830,23540,22320,21170,20080,19060,18100,17190,16330,15520,14750,14030,13340,12700,12090,11510,10960,10440,9950,9485,9045,8630,8230,7855,7500,7160,6840,6535,6245,5970,5710,5460,5225,5000,4787,4583,4389,4204,4029])
	#for i in range(len(Temp_x)):
	#    Resis_y = np.append(Resis_y,Resistance_calc(Temp_x[i]))
	Temperature_R = np.interp(R, np.sort(Resis_y), -np.sort(Temp_x))
	#plt.plot(Temp_x, Resis_y, 'o')                                                                                                                                                                                                           
	#plt.show()                                                                                                                                                                                                                               
	return Temperature_R

def Temp_calc(R): #Function to calculate temperature for any resistance                                                                                                                                                                       
	Temp_x = np.linspace(-30, 30, num=100) #Points to be used for interpolation                                                                                                                                                               
	Resis_y = np.array([])
	for i in range(len(Temp_x)):
		Resis_y = np.append(Resis_y,Resistance_calc(Temp_x[i]))
	Temperature_R = np.interp(R, Resis_y, Temp_x)
	#plt.plot(Temp_x, Resis_y, 'o')                                                                                                                                                                                                           
	#plt.show()                                                                                                                                                                                                                               
	return Temperature_R

def ConvertEnv(timestamp):
	Resis20, Voltage1, Current1 = GetEnvMeas(timestamp)
	if Resis20 != -1 and Resis20 != 0:
		Temp20 = round(Temp_calc(Resis20),2)
	else: 
		Temp20 = -999
	return Temp20, Voltage1, Current1