#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from services.ConfigFile import ConfigFile

class ConfigService(object):
   def __init__(self, os = None):
       self.os = os
       self.globalConfig = ConfigFile(self.getAppPath() + "/etc/global.cfg")
       if(os == "Mac"):
           self.customConfig = ConfigFile(self.getAppPath() + "/etc/playonmac.cfg")
       if(os == "Linux"):
           self.customConfig = ConfigFile(self.getAppPath() + "/etc/playonlinux.cfg")
          
       self.userConfig = ConfigFile(self.getUserRoot() + "/playonlinux.cfg")
       self.fileTypes = ConfigFile(self.getUserRoot() + "/extensions.cfg")
              
   def getSetting(self, item):
       # Read in priority : POL_USER_ROOT/playonlinux.cfg, PLAYONLINUX/etc/playon[linux/mac].cfg, PLAYONLINUX/etc/global.cfg, and return the data
       if(self.userConfig.getSetting(item) != ""):
           return self.userConfig.getSetting(item)
       elif(self.os != None and self.customConfig.getSetting(item) != ""):
           return self.customConfig.getSetting(item)
       elif(self.globalConfig.getSetting(item) != ""):
           return self.globalConfig.getSetting(item)
       else:
           return ""    
 
   def setSetting(self, item, value):
       self.userConfig.setSetting(item, value)