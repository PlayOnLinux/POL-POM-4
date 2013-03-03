#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

from lib.Context import Context
from lib.System import System
from lib.ConfigFile import GlobalConfigFile 
from lib.ConfigFile import CustomConfigFile


import os, string, wx, gettext

class Environement(object):
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
          self.initEnvironement()
     
   def initEnvironement(self):  
      self.system = System()
      
      
      self.pol_os = self.getEnv("POL_OS")
     
      if(self.pol_os == ""):
          print "ERROR ! Please define POL_OS environment var first."
          self.system.hardExit(1)
         
      
         
   def getAppPath(self):
          return os.path.realpath(os.path.realpath(__file__)+"/../../../") 
   
   def setEnv(self, var, content):
        os.environ[var] = str(content)
               
   def getEnv(self, var):
      try :
         return os.environ[var]
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
       
       
   # Create a context from the environement
   def createContext(self):
       Context().setOS(self.pol_os)
       Context().setAppPath(self.getAppPath()) 
       Context().setUserRoot(self.getUserRoot()) 
       
       if(self.getArch() == "x86_64" and self.pol_os == "Linux"):
           Context().set64bit(True)
       else:
           Context().set64bit(False)
           
       self.globalConfig = GlobalConfigFile()
       self.customConfig = CustomConfigFile()
       
       
       isDebian = self.globalConfig.getSetting("DEBIAN_PACKAGE") == "TRUE"
       Context().setDebianPackage(isDebian)
       Context().setAppVersion(self.globalConfig.getSetting("VERSION"))
       Context().setAppName(self.customConfig.getSetting("APPLICATION_TITLE"))
       