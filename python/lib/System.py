#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2011 - Quentin PARIS

import os

class System(object):
    
   
   def __init__(self):
      return True

   @staticmethod
   def isRunAsRoot():
       return (os.popen("id -u").read() == "0\n" or os.popen("id -u").read() == "0")
      
   