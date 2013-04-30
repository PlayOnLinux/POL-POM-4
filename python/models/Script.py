#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os

# PlayOnLinux
from models.Executable import Executable
from models.PlayOnLinux import PlayOnLinux
from models.Environement import Environement
from models.GuiServer import GuiServer

class ErrBadSignature(Exception):
   def __str__(self):
      return repr(_("The signature of the script is wrong"))

class Script(Executable):
   def __init__(self, scriptPath, args):
      args = args[:]
      args.insert(0, scriptPath)
      Executable.__init__(self, "bash", args)
      self.needSignature = True

      
   def checkSignature(self):    
       # Fixme
       return True
       
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
      Script.__init__(self, PlayOnLinux().getAppPath()+"/bash/"+path, args)
      self.needSignature = False

      
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

  
class POLUpdaterScript(PrivateScript):
     def __init__(self, parent):
         self.parent = parent
         PrivateScript.__init__(self, "pol_update_list", [])   
             
     def parseScriptOut(self, line):
         if(line.isdigit()):
             self.parent.sendPercentage(int(line)) 