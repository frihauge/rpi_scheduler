import schedule
import time
import sys
import threading
from app.ftpmodule import FileCtrl
from ina219 import INA219



class RPI_Sceduler:

    def __init__(self):
       shunt_ohms = 0.1
       self.address = 40
       self.max_expected_amps = 0.6
       self.ina = None
       self.fc = None
       self.measurement =dict()
  
       self.initINA219()
       self.ConnectFileCtrl()   

    def makemeasurements(self):
       print "\nMake Measurement"
       i = 0
       v = 0
       if self.ina is not None:
           v = self.ina.voltage()
           i = self.ina.current()
           p = self.ina.power()
           print("Ina not initializied")
       print ("Current read from sonsor read {}".format(i))
       print ("Voltage read from sonsor read {}".format(v))
       
       timesring = time.strftime("%Y%m%d-%H%M%S")
       self.measurement[timesring] = dict()
       self.measurement[timesring]['Current'] = i 
       self.measurement[timesring]['Voltage'] = v 
       
      
        
       if self.fc is not None:
           self.fc.UpdateLocalDataFile(self.measurement)
       print ('Measured Current:{0:.2f}'.format(i))

    def uploadFile(self):
        if self.fc is not None:
            #USB device need to be mounted
            print "\nCopy file to USB device"
            self.fc.CopyFileToUSB("/media/USB")
            if self.fc.UploadLocalDataFile() == True:
               self.measurement = None
               self.measurement =dict()
               print "\nUpload File"
            else:
               print "\nUpload File failed"
               os.remove('localfiles//'+self.RpiSerialNumber+'_l.json') 
              
        
    def ConnectFileCtrl(self):
        self.fc = FileCtrl()
        return 
    
    def initINA219(self):
        self.ina = INA219(shunt_ohms=0.1,
                     max_expected_amps = 0.6,
                     address=0x40)
        self.ina.configure(self.ina.RANGE_16V)

time_start = time.time()
seconds = 0
minutes = 0

def Uploadingevent():
    print("Uploading file to FTP...")
    rpi_Sch.uploadFile()
def Measureevent():
    print("Making measurement...")
    rpi_Sch.makemeasurements()
    
print ("Current shunt scheduled measurement")

rpi_Sch = RPI_Sceduler()
schedule.every(30).seconds.do(Measureevent)
#schedule.every(45).seconds.do(Uploadingevent)
schedule.every().hour.do(Uploadingevent)
print ("Startup complete/n")
print ("Measurement  run every 30 sec and upload every 1 hour")

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
        
        
        if minutes >= 60:
            minutes = 0
    except KeyboardInterrupt, e:
        break