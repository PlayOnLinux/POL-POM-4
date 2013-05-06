#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS


import os, string, wx, gettext


# Exceptions
class ErrNoPOLOS(Exception):
   def __str__(self):
      return repr(_("POL_OS is not set"))      
      
class ErrUnknownOS(Exception):
   def __str__(self):
      return repr(_("Unknown OS"))     
       
# This class read information from environement
class Environment(object):    
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
       
   def getOSCodeName(self):
      if(self.getOS() == "Mac"):
          return "darwin"
      if(self.getOS() == "Linux"):
          return "linux"
      raise ErrUnknownOS
         
   def getAppPath(self): 
      return os.path.realpath(os.path.realpath(__file__)+"/../../../") 
   
   def setEnv(self, var, content):
      self.customEnv[var] = str(content)
               
   def getEnv(self, var):
      try :
         return self.customEnv[var]
      except KeyError:
         return ""
    
   def is64bits(self):
       return (self.getArch() == "x86_64" and self.getOS() == "Linux")
        
   def getArch(self):
       archi = string.split(self.getEnv("MACHTYPE"),"-")
       return archi[0]
   
   def getUserRoot(self):
       if(self.pol_os == "Linux"):
          return self.getEnv("HOME")+"/.PlayOnLinux/"
          
       if(self.pol_os == "Mac"):
          return self.getEnv("HOME")+"/Library/PlayOnMac/"
       
   def isGIT(self):
       return os.path.exists(self.getAppPath()+"/.git/")