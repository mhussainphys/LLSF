import socket
import sys
import time

ip_address = "192.168.133.50"
runFileName = "/home/daq/otsdaq/srcs/otsdaq_cmstiming/Data_2018_09_September/ServiceData/RunNumber/OtherRuns0NextRunNumber.txt"

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

def stop_ots(Delay=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = "OtherRuns0,Stop"
    sock.sendto(MESSAGE, (ip_address, 8000))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Stop: received message:", data
    if Delay: time.sleep(5)
