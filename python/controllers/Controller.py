#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from models.PlayOnLinux import PlayOnLinux
from models.Script import PrivateScript
from models.SystemCheck import SystemCheck
from models.GuiServer import GuiServer

class Controller(object):
   instance = None    
   
   def __new__(myClass):
       if(myClass.instance is None):
           myClass.instance = object.__new__(myClass)
       return myClass.instance
       
   def __init__(self):
      try: 
          self.alreadyInit          
      except AttributeError:
          self.alreadyInit = True
       
       
   # Class content
   def appStartupBeforeServer(self):
       startupScript = PrivateScript("startup")
       startupScript.start()
       startupScript.waitProcessEnd()
       SystemCheck().doFullCheck()
       
   def appStartupAfterServer(self):
       startupScript = PrivateScript("startup_after_server")
       startupScript.start()
       
   # Server managing
   def getServer(self):
       return PlayOnLinux().getServer()
           
   def getServerQueue(self):
       return PlayOnLinux().getServerQueue()
       
   def getServerState(self):
       return PlayOnLinux().getState()
       
       
   # 
   def getAppName(self):
       return PlayOnLinux().getAppName()

   def isDebianPackage(self):
       return PlayOnLinux().isDebianPackage()
       
   def getAppPath(self):
       return PlayOnLinux().getAppPath()
     
   #
   def setSetting(self, item, value):
       configFile = UserConfigFile()
       configFile.setSetting(item, value)
       
   def getSetting(self, item):
       return PlayOnLinux().getSetting(item)
       
   # 
   def openFile(self, filename):
       openedFile = LocalFile(filename)
       openedFile.openCleverWay()
       
   # 
   def openUrl(self, url):
       self.urlHandler = PrivateScript("playonlinux-url_handler",[url])
       self.urlHandler.run()