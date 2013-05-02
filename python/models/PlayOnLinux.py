#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

import os, random, sys, string, gettext, locale

from services.ConfigService import *
from services.Environment import Environment

# Singleton
class PlayOnLinux(object):
   def __init__(self): 
      self.environment = Environment()
      self.configService = ConfigService()
      self.version = self.configService.getSetting("VERSION")        

   # Server managing
   def getServer(self):
       try:
           return self.server
       except AttributeError:
           self.server = GuiServer()
           return self.server
           
   def getServerQueue(self):
       return self.getServer.getQueue()
       
   def getServerState(self):
       return self.getServer.getState()
       
                  
   # Getters and setters
   def getAppVersion(self):
       return self.configService.getSetting("VERSION")
        
   def isUpToDate(self):
       try:
           return self.upToDate
       except AttributeError:
           return True