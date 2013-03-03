#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

from lib.Context import Context
from lib.System import System
from lib.ConfigFile import GlobalConfigFile 
from lib.ConfigFile import CustomConfigFile
from lib.ConfigFile import UserConfigFile


import os, string, wx, gettext


# Exceptions
class ErrNoPOLOS(Exception):
   def __str__(self):
      return repr(_("POL_OS is not set"))

class ErrContextNotInitialized(Exception):
   def __str__(self):
      return repr(_("Context need to be created to use this function"))
      
      
      
      
# This class read information from environement (PlayOnLinux config files, OS, ...)
class Environement(object):    
   def __init__(self):
       
       self.customEnv = os.environ.copy()
       self.pol_os = self.getOS()
    
   # Return environement state
   def get(self):
       return self.customEnv
          
   def getOS(self):
       current_os = self.getEnv("POL_OS")
       if(current_os == ""):
           raise ErrNoPOLOS
       return current_os
           
   def getAppPath(self): 
      return os.path.realpath(os.path.realpath(__file__)+"/../../../") 
   
   def setEnv(self, var, content):
      self.customEnv[var] = str(content)
               
   def getEnv(self, var):
      try :
         return self.customEnv[var]
      except KeyError:
         return ""
    

        
   def getArch(self):
       archi = string.split(self.getEnv("MACHTYPE"),"-")
       return archi[0]
   
   def getUserRoot(self):
       if(self.pol_os == "Linux"):
          return self.getEnv("HOME")+"/.PlayOnLinux/"
          
       if(self.pol_os == "Mac"):
          return self.getEnv("HOME")+"/Library/PlayOnMac/"
       
 
   def getSetting(self, item):
       # Read in priority : POL_USER_ROOT/playonlinux.cfg, PLAYONLINUX/etc/playon[linux/mac].cfg, PLAYONLINUX/etc/global.cfg, and return the data
       if(not Context().isCreated()):
           raise ErrContextNotInitialized
           
       self.globalConfig = GlobalConfigFile()
       self.customConfig = CustomConfigFile()
       self.userConfig = UserConfigFile()
       
       # Read User config file only if the context has been initialized
       if(self.userConfig.getSetting(item) != ""):
           return self.userConfig.getSetting(item)
       elif(self.customConfig.getSetting(item) != ""):
           return self.customConfig.getSetting(item)
       elif(self.globalConfig.getSetting(item) != ""):
           return self.globalConfig.getSetting(item)
       else:
           return ""
           
   # Create a context from the environement
   def createContext(self):
       Context().setOS(self.pol_os)
       Context().setAppPath(self.getAppPath()) 
       Context().setUserRoot(self.getUserRoot()) 
       
       
       if(self.getArch() == "x86_64" and self.pol_os == "Linux"):
           Context().set64bit(True)
       else:
           Context().set64bit(False)
       
       Context().setCreated()
       
       isDebian = self.getSetting("DEBIAN_PACKAGE") == "TRUE"
       
       Context().setDebianPackage(isDebian)
       Context().setAppVersion(self.getSetting("VERSION"))
       Context().setAppName(self.getSetting("APPLICATION_TITLE"))
       