#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os
from lib.Executable import Executable


from lib.Context import Context

from lib.ConfigFile import GlobalConfigFile 
from lib.ConfigFile import CustomConfigFile
from lib.ConfigFile import UserConfigFile

from lib.Environement import Environement
from lib.GuiServer import GuiServer

class ErrBadSignature(Exception):
   def __str__(self):
      return repr(_("The signature of the script is wrong"))

class Script(Executable):
   def __init__(self, path, args):
      self.path = path
      self.args = args
      self.needSignature = True
      self.execEnv = Environement()
      self.setEnv()
      
   def checkSignature(self):    
       # Fixme
       return True
       
   def getProgramArray(self):
       args = self.args
       args.insert(0,self.path)
       args.insert(0,"bash")
       return args
       
   def run(self):  
       if(self.checkSignature() or not self.needSignature):
          Executable.run(self)
       else:
          raise ErrBadSignature

   def runPoll(self):  
       if(self.checkSignature() or not self.needSignature):
           Executable.runPoll(self)
       else:
          raise ErrBadSignature
           

class PrivateScript(Script):
   def __init__(self, path, args = []):
      self.context = Context()
      
      self.path = self.context.getAppPath()+"/bash/"+path
      self.args = args
      self.needSignature = False
      self.execEnv = Environement()
      self.setEnv()
      
class GUIScript(Script):
    def setEnv(self):
        Script.setEnv(self)
        # Set by the GUI server
        
        self.execEnv.setEnv("POL_PORT", GuiServer().getRunningPort())
        self.execEnv.setEnv("POL_COOKIE", GuiServer().getCookie())
  
        
        
class PrivateGUIScript(PrivateScript):
    def setEnv(self):
        PrivateScript.setEnv(self)
        
        # Set by the GUI server
        self.execEnv.setEnv("POL_PORT", GuiServer().getRunningPort())
        self.execEnv.setEnv("POL_COOKIE", GuiServer().getCookie())

  
        