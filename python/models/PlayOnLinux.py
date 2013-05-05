#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

import os, random, sys, string, gettext, locale

from services.ConfigService import *
from services.Environment import Environment

from models.Version import Version

class PlayOnLinux(object):
   def __init__(self): 
      self.environment = Environment()
      self.configService = ConfigService()
      self.version = self.configService.getSetting("VERSION")        

                  
   # Getters and setters
   def getAppVersion(self):
       return Version(self.configService.getSetting("VERSION"))
        
   def isUpToDate(self):
       try:
           return self.upToDate
       except AttributeError:
           return True