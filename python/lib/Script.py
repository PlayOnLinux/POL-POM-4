#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os

# PlayOnLinux libs
from Context import Context

class Script(object):
   def __init__(self, path, args):
      self.path = path
      self.args = args
      self.needSignature = True
      return True
      
   # Fixme
   def checkSignature(self): 
                
       # Fixme
       return True
       
   def getProgramArray(self, args = []):
       args.insert(0,self.path)
       args.insert(0,"bash")
       return args
       
   def run(self):
       if(self.checkSignature() or not self.needSignature):
          try:
               returncode = subprocess.call(self.getProgramArray(self.args))
               return returnCode
          
          except:
              return 255
       else:
          return 300 # Wrong signature

   def runPoll(self):
       if(self.checkSignature() or not self.needSignature):
           return subprocess.Popen(self.getProgramArray(self.args), stdout = subprocess.PIPE, preexec_fn = lambda: os.setpgid(os.getpid(), os.getpid()))

class PrivateScript(Script):
   def __init__(self, path, args = []):
      self.context = Context()
      self.path = self.context.getAppPath()+"/bash/"+path
      self.args = args
      self.needSignature = False
  