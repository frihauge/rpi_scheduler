import schedule
import time
import sys
import threading
from app.ftpmodule import FileCtrl
from ina219 import INA219





class RPI_Sceduler:

    def __init__(self):
       #Setting for INA219
       self.shunt_ohms = 0.0015
       self.address = 0x40
       self.max_expected_amps = 50
       
       # Vars for objects
       self.ina = None
       self.fc = None
       self.measurement =dict()
  
       self.initINA219()
       #Init file control incl. FTP upload
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

    def uploadFile(self):
        if self.fc is not None:
            #USB device need to be mounted
            print "\nCopy file to USB device"
            self.fc.CopyFileToUSB("/media/usb")
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
        
        self.ina = INA219(shunt_ohms=self.shunt_ohms,
                     max_expected_amps = self.max_expected_amps,
                     address=self.address)
        self.ina.configure(self.ina.RANGE_16V)#,gain=self.ina.GAIN_AUTO,
#              bus_adc=self.ina.ADC_128SAMP,
#              shunt_adc=self.ina.ADC_128SAMP)
#Main start here 

#Timerevents
def Uploadingevent():
    print("Uploading file to FTP...")
    rpi_Sch.uploadFile()
def Measureevent():
    print("Making measurement...")
    rpi_Sch.makemeasurements()
        
print ("Current shunt scheduled measurement")

#Create RPI_Sceduler object
rpi_Sch = RPI_Sceduler()
#Setup a 30 sec timer event
schedule.every(30).seconds.do(Measureevent)
#Setup a 1 hour timer event
schedule.every().hour.do(Uploadingevent)
print ("Startup complete/n")
print ("Measurement  run every 30 sec and upload every 1 hour")

while True:
    try:
        #Wait for timer events
        schedule.run_pending()
      
    except KeyboardInterrupt, e:
        break