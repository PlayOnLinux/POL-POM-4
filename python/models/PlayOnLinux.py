#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

import os, random, sys, string, gettext, locale

from models.Environment import Environment
from services.ConfigService import *

# Singleton
class PlayOnLinux(object):
   def __init__(self): 
      self.environment = Environment()
      ConfigService.register(self.environment)
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
        
   def getEnv(self):
       return self.environment
       
   def getAppVersion(self):
       return self.version
      
   def isDebianPackage(self):
       return (self.configService.getSetting("DEBIAN_PACKAGE") == "TRUE")
        
   def isUpToDate(self):
       try:
           return self.upToDate
       except AttributeError:
           return True