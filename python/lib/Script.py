#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess

# PlayOnLinux libs
from Context import Context

class Script(object):
   def __init__(self, path):
      self.path = path
      return True
      
   # Fixme
   def checkSignature(self): 
       return True
       
   def run(self, args):
       try:
          args.prepend(self.path)
          args.prepend("bash")
          returncode = subprocess.call(args)
          return returnCode
          
       except:
          return 255
       
       
class PrivateScript(Script):
   def __init__(self, path):
      self.context = Context()
      self.path = self.context.getAppPath()+"/bash/"+path
     
   # No need to check the signature, because it is an internal script
   def checkSignature(self):
       return True