echo "stop" > Scan.status
echo "0" > /home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/ScanInitiate.txt
echo "0" > /home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/MotorReadyToMove.txt
echo "0" > /home/daq/LaserScan/LaserScanWindows/MotorControlTextFiles/LastIterationBool.txt
echo "######## Stopping the autopilot gently! #######"