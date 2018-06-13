from ftplib import FTP
import logging

class FTPConnect:
  server="77.68.194.39"
  user="OSRA"
  password="R3m0T3"
  SettingsFileName="settings.json"
  cScriptDoneFolder= "ScriptDone"
  cScriptWaitingFolder = "ScriptWaiting"
  def chdir(self,dir):
    if self.directory_exists(dir) is False: # Create it if not exsist
      self.ftp.mkd(dir)
      self.ftp.mkd(dir+"//ScriptDone")
      self.ftp.mkd(dir+"//ScriptWaiting")
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
     logging.warning("FTP logging in")
    except Exception,e:
     print e
     return False
    else:
      print "FTP Connect success"
      return True

  def __init__(self,serienummer):
    self.serienummer = serienummer
    print self.serienummer
    try:
      self.connect()
      self.chdir(self.serienummer)
    except Exception,e:
      print e
    else:
     self.data = []

  def UploadFile(self, file,filename):
    self.ftp.storbinary('STOR ' +filename, file)
  
  def moveConfigfile(self,DevUI,State):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    if State:
      finalfilename = "{}//{}_Pass.json".format(self.cScriptDoneFolder,timestr)
    else:
      finalfilename = "{}//{}_Error.json".format(self.cScriptDoneFolder,timestr)
    self.ftp.cwd("/"+DevUI)
    print(self.ftp.pwd())
    self.ftp.rename("{}//{}.json".format(self.cScriptWaitingFolder,DevUI),finalfilename)

   
  def GetBlindSettingsFile(self,filename):
    logging.debug("Get Setting File")
    files = self.ftp.dir()
    self.make_sure_path_exists("localfiles")
    gFile = open("localfiles//"+filename, "wb") ##Create Local file
    self.ftp.retrbinary("RETR " + filename, lambda s, w=gFile.write: w(s+"\n"))
    gFile = open("localfiles//"+filename, "r")##Open local file
    buff = gFile.read()
    return buff

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
    self.BlindCtrlSerialNumber = self.getserial() 
           
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
  
  def FtpMainGetFile(self):
    serienummer = self.BlindCtrlSerialNumber
    logging.debug('Serial Number is: '+ serienummer)
    lFtp = FTPConnect(serienummer)
    if lFtp.GetFTPFileExist(serienummer+'.json'):
      lFtp.GetBlindSettingsFile(serienummer+'.json')
      lFtp.Close()
      return True
    #else:
    lFtp.Close()
    return False

  def FtpMainFileExist(self):
    serienummer = self.BlindCtrlSerialNumber
    logging.debug('Serial Number is: '+ serienummer)
    lFtp = FTPConnect(serienummer)
    state =  lFtp.GetFTPFileExist(serienummer+'.json')
    lFtp.Close()
    return state
    

  def CreateLocalDataFile(self):
      
      Ch = Commandhandler()
      StrAll_Modules=Ch.ScanNet()
      # create blinddataobject
      print("Parse All Data from modules")
      BCD = BlindCtrlData(self.BlindCtrlSerialNumber)
      BCD.ParseObjects(StrAll_Modules)
      with open("localfiles//"+self.BlindCtrlSerialNumber+"_l.json", "w") as outfile:
        json.dump(BCD, outfile,indent=2, sort_keys=True, default=methodcaller("jsondefault"))
      print("Parse done")
  
  def UploadLocalDataFile(self):
      serienummer = self.BlindCtrlSerialNumber
      lFtp = FTPConnect(serienummer)
      print('Upload Local file to FTP')
      file = open('localfiles//'+self.BlindCtrlSerialNumber+'_l.json','rb')
      lFtp.UploadFile(file,self.BlindCtrlSerialNumber+'.json')
      file.close()
      lFtp.Close()

  def GetWaitingConfigFile(self):
      serienummer = self.BlindCtrlSerialNumber
      self.lFtp = FTPConnect(serienummer)
      self.lFtp.ftp.cwd("ScriptWaiting")
      logging.debug("See if file is waiting")
      files = self.lFtp.ftp.dir()
      state =  self.lFtp.GetFTPFileExist(serienummer+'.json')
      if state:
        self.waitingfile = self.lFtp.GetBlindSettingsFile(serienummer+'.json')
      return state    

  def programNewSettings(self):
      status = False
      Ch = Commandhandler()
    #  print(self.updateBlindObj.BlindCtrls)
      for blctrl in self.updateBlindObj.BlindCtrls:
        status = Ch.ProgramCtrl(blctrl)
        if status == False:
          return status 
      return status 
  
  def GetAndExecuteWaitingFile(self):
      if self.GetWaitingConfigFile():
        parsestate=False
        print("Load new file")
        UpdateBlinddata = BlindCtrlData(self.BlindCtrlSerialNumber)
        self.updateBlindObj = UpdateBlinddata.FillObjWithJson(self.waitingfile)
        if self.updateBlindObj.DoUpdate and self.updateBlindObj.DeviceNumber == self.BlindCtrlSerialNumber:
            print ("Do update")
            parsestate = True
            self.programNewSettings()
            #update main file 
            self.CreateLocalDataFile()
            print("Upload local file to FTP")
            self.UploadLocalDataFile()
        else:
            parsestate = False
            print("Mark file as error and move file to ")    
 #move file to done folder
        self.lFtp.moveConfigfile(self.BlindCtrlSerialNumber,parsestate)     

      else:
        print("No waiting file found")        
      
      self.lFtp.Close()
        
  def RunUpdate(self):
    try:   
      if self.FtpMainFileExist() == True:
         self.GetAndExecuteWaitingFile()
         return("File OK")
      else:
        print("No Valid FTP file availble, create a local file from devicedata")
        self.CreateLocalDataFile()
        print("Upload local file to FTP")
        self.UploadLocalDataFile()
    except Exception, e:
      print (e)   
     # return ("")

      
      

        
        