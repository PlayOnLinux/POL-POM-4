#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

import os, random, sys, string, gettext, locale

from models.Environement import Environement
from models.ConfigFile import *

# Singleton
class PlayOnLinux(object):
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
          self.registeredPid = [] # List of bash pids belonging to POL 
          self.windowOpened = 0   # Number of POL_SetupWindow opened    
          self.environement = Environement()
          self.globalConfig = ConfigFile(self.getAppPath() + "/etc/global.cfg")
          if(PlayOnLinux().getOS() == "Mac"):
              self.customConfig = ConfigFile(self.getAppPath() + "/etc/playonmac.cfg")
          if(PlayOnLinux().getOS() == "Linux"):
              self.customConfig = ConfigFile(self.getAppPath() + "/etc/playonlinux.cfg")
              
          self.userConfig = ConfigFile(self.getUserRoot() + "/playonlinux.cfg")
          self.fileTypes = ConfigFile(self.getUserRoot() + "/extensions.cfg")
                  
          self.pol_os = self.environement.getOS()
          self.appPath = self.environement.getAppPath()
          self.userRoot = self.environement.getUserRoot()
      
   def getSetting(self, item):
       # Read in priority : POL_USER_ROOT/playonlinux.cfg, PLAYONLINUX/etc/playon[linux/mac].cfg, PLAYONLINUX/etc/global.cfg, and return the data
           
       # Read User config file only if the context has been initialized
       if(self.userConfig.getSetting(item) != ""):
           return self.userConfig.getSetting(item)
       elif(self.customConfig.getSetting(item) != ""):
           return self.customConfig.getSetting(item)
       elif(self.globalConfig.getSetting(item) != ""):
           return self.globalConfig.getSetting(item)
       else:
           return ""
                 

   # Server managing
   def getServer(self):
       try:
           return self.server
       except AttributeError:
           self.server = GuiServer()
           return self.server
           
   def getServerQueue(self):
       return self.getServer.getQueue()
       
   def getServerState(self):
       return self.getServer.getState()
       
                  
   # Getters and setters
   
   # PlayOnLinux OS (Linux or Mac)
   def getOS(self):
       return self.pol_os
         
   def getAppEnv(self):
       return self.environement
       
   def getCodeName(self):
       if(self.getOS == "Linux"):
           return "linux"
       if(self.getOS == "Mac"):
           return "darwin"
         
   # App path 
   def getAppPath(self):
      return self.appPath
        
         
   # User root
   def getUserRoot(self):
       return self.userRoot
     
         
   # 64 bits
   def is64bit(self):
       return (self.environement.getArch() == "x86_64" and self.environement.getOS() == "Linux")
  
   
   # Application name (Exemple : PlayOnLinux)
   def getAppName(self):
       return self.getSetting("APPLICATION_TITLE")
       
   def getAppVersion(self):
       try: 
           return self.version
       except AttributeError:
           self.version = Version(self.getSetting("VERSION"))
           return self.version
       
   def isDebianPackage(self):
       return (self.getSetting("DEBIAN_PACKAGE") == "TRUE")
       
   def getRegisteredPids(self):
       return self.registeredPid
      
   def getWindowOpened(self):
       return self.windowOpened
      
   def incWindowOpened(self):
       self.windowOpened += 1
   
   def decWindowOpened(self):
       self.windowOpened -= 1  

   def registerPid(self, pid):
       self.registeredPid.append(pid)
       
   def setUpToDate(self, value):
       self.upToDate = value
       
   def isUpToDate(self):
       try:
           return self.upToDate
       except AttributeError:
           return True