import time
import sys
import threading
from app import ftpmodule
from ina219 import INA219




class RPI_Sceduler:

    def __init__(self):
       shunt_ohms = 0.1
       self.address = 40
       self.max_expected_amps = 0.6
       self.ina = None
       self.initINA219()
       self.ConnectFTP(ftphost = '52.214.152.160',user='greentech',pwd='jf7834#)kc!_')   
   
    def makemeasurements(self):
       print "\nMake Measurement"
       v = self.ina.voltage()
       i = self.ina.current()
       p = self.ina.power()
       print ('Measured Current:{0:.2f}'.format(i))

    def uploadFile(self):
       print "\nUpload File"
      
    def ConnectFTP(self,ftphost ,user,pwd): 
        return 
    
    def initINA219():
        self.ina = INA219(shunt_ohms=0.1,
                     max_expected_amps = 0.6,
                     address=0x40)

time_start = time.time()
seconds = 0
minutes = 0

print ("Current shunt scheduled measurement")
rpi_Sch = RPI_Sceduler()

while True:
    try:
        sys.stdout.write("\r{minutes} Minutes {seconds} Seconds".format(minutes=minutes, seconds=seconds))
        sys.stdout.flush()
        time.sleep(1)
        seconds = int(time.time() - time_start) - minutes * 60

 
        if seconds == 30:
            rpi_Sch.makemeasurements()
        if seconds >= 60:
            rpi_Sch.makemeasurements()
            minutes += 1
            seconds = 0
        if minutes >= 60:
            rpi_Sch.uploadFile()
            minutes = 0
    except KeyboardInterrupt, e:
        break