#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os

# PlayOnLinux libs
from Context import Context

class Script(object):
   def __init__(self, path):
      self.path = path
      self.needSignature = True
      return True
      
   # Fixme
   def checkSignature(self): 
       if(self.needSignature == False):
           return True
           
       # Fixme
       return True
       
   def getProgramArray(self, args = []):
       args.insert(0,self.path)
       args.insert(0,"bash")
       return args
       
   def run(self, args):
       try:
          returncode = subprocess.call(self.getProgramArray(args))
          return returnCode
          
       except:
          return 255

   def runPoll(self, args = []):
       return subprocess.Popen(self.getProgramArray(args), stdout = subprocess.PIPE, preexec_fn = lambda: os.setpgid(os.getpid(), os.getpid()))
       
class PrivateScript(Script):
   def __init__(self, path):
      self.context = Context()
      self.path = self.context.getAppPath()+"/bash/"+path
      self.needSignature = False
     
   # No need to check the signature, because it is an internal script
   def checkSignature(self):
       return True