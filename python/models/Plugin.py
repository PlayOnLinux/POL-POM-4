#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, os

# playonlinux imports
from services.Environment import Environment



class Plugin(object):
   def __init__(self, name):
       self.name = name
       self.env = Environment()
       
   def getName(self):
       return self.name

   def getPath(self):
       return self.env.getUserRoot()+"/plugins/"+self.getName()
       
   def isEnabled(self):
       return os.path.exists(self.getPath()+"/enabled")