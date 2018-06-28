import os
import shutil
import io
from operator import methodcaller
import json
from ftplib import FTP
import time

class FTPConnect:
  server="52.214.152.160"
  user="greentech"
  password="jf7834#)kc!_"

  def chdir(self,dir):
    if self.directory_exists(dir) is False: # Create it if not exsist
      self.ftp.mkd(dir)
    self.ftp.cwd(dir)

  def directory_exists(self, directory_name):
    filelist = []
    self.ftp.retrlines('LIST',filelist.append)
    for f in filelist:
        if f.split()[-1] == directory_name:
            return True
    return False

  def Close(self):
    try:
     self.ftp.quit()
    except Exception,e:
     print e
    else:
      print "FTP Close success"

  def connect(self):
    try:
     self.ftp = FTP(self.server, timeout=5)
     self.ftp.login(self.user,self.password)
     print("FTP logging in")
    except Exception,e:
     print e
     return False
    else:
      print "FTP Connect success"
      return True

  def __init__(self,serienummer):
    self.serienummer = serienummer
    print self.serienummer
#    try:
      #self.connect()
      #self.chdir(self.serienummer)
#    except Exception,e:
    #  print e
   # else:
    self.data = []

  def UploadFile(self, file,filename):
    self.ftp.storbinary('STOR ' +filename, file)
  

   


  def GetFTPFileExist(self,file_name):
    filelist = []
    self.ftp.retrlines('LIST',filelist.append)
    for f in filelist:
        if f.split()[-1] == file_name:
            return True
    return False

  def make_sure_path_exists(self,path):
      try:
          os.makedirs(path)
      except OSError as exception:
          if exception.errno != errno.EEXIST:
              raise



class FileCtrl:
     
  def __init__(self):
    #Get Serial from RPI   
    self.RpiSerialNumber = self.getserial() 
    if not os.path.exists('localfiles'):
        os.makedirs('localfiles')
        
    
           
  def getserial(self):
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
      f = open('/proc/cpuinfo','r')
      for line in f:
        if line[0:6]=='Serial':
          cpuserial = line[10:26]
      f.close()
    except:
      cpuserial = "ERROR000000000"
    return cpuserial
  
    

  def UpdateLocalDataFile(self,measumentdata):
    if os.path.isfile('localfiles//'+self.RpiSerialNumber+'_l.json') and os.access('localfiles//'+self.RpiSerialNumber+'_l.json', os.R_OK):
        # checks if file exists
        print ("File exists and is readable")
    else:
        print ("Either file is missing or is not readable, creating file...")
        self.CreateLocalDataFile()
    print('RPI serial:' + self.RpiSerialNumber)
    print measumentdata
    with open('localfiles//'+self.RpiSerialNumber+'_l.json','r+') as outfile:
        #  data = json.load(outfile)
        #  data.update(measumentdata)
        #  print data  
        json.dump(measumentdata, outfile)
   
    print("Parse done")
  
  def CreateLocalDataFile(self):
      with open('localfiles//'+self.RpiSerialNumber+'_l.json','w') as outfile:
          json.dump({}, outfile)
      print("Parse done")
      
  def UploadLocalDataFile(self, copytolocal=False):
      serienummer = self.RpiSerialNumber
      lFtp = FTPConnect(serienummer)
      if lFtp.connect() == True:
          print('Upload Local file to FTP')
          timestr = time.strftime("%Y%m%d-%H%M%S")
          file = open('localfiles//'+self.RpiSerialNumber+'_l.json','rb')
          filename = self.RpiSerialNumber+'_'+timestr+'.json'
          lFtp.UploadFile(file,filename)
          file.close()
          lFtp.Close()     #delete file
          return True
      else:
          return False    
    
  def CopyFileToUSB(self,destination):
      source = '/home/pi/programs/rpi_scheduler/localfiles/'+self.RpiSerialNumber+'_l.json'
      timestr = time.strftime("%Y%m%d-%H%M%S")
      filename = self.RpiSerialNumber+'_'+timestr+'.json'
      print("Copy file " + source + " to "+ destination+ '/'+filename)
      try:
          shutil.copy2(source, destination+ '/'+filename)
      except shutil.Error as e:
          print("Error: %s" % e)
              # E.g. source or destination does not exist
      except IOError as e:
          print("Error: %s" % e.strerror)




      
      

        
        