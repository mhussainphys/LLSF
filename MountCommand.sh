#Go to the folder's properties in windows to share the folder with proper permissions. And then when both pc's are on the same network, do:
mkdir LaserScanWindows
mkdir e
sudo mount.cifs //192.168.133.52/LaserScan /home/daq/LaserScan/LaserScanWindows/ -o user=apresyan,uid=1000,gid=1000
sudo mount.cifs //192.168.133.52/e /home/daq/LaserScan/e/ -o user=apresyan,uid=1000,gid=1000