#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

class Script(object):
    
   def __init__(self, path):
      self.path = path
      return True
      
   def checkSignature(self):
       return True
       
   def run(self, args):
       return True