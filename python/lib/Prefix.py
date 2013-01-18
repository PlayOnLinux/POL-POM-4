#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports

# playonlinux imports
import Variables, getConfigFile

PREFIXES_PATH = Variables.pol_user_root+"/wineprefix/"

class Prefix()
   def __init__(self, prefixName):
       self.selectedPrefix = prefixName;
       
   def getConfigFilePath(self):
       return self.getPath()+"/playonlinux.cfg";

   def getConfigFile(self):
       # Return the config file object corresponding to the config file in the prefix
       return getConfigFile(self.getConfigFilePath());
       
   def getPath(self):
       return PREFIXES_PATH+self.selectedPrefix;
             
   def exists(self):
       # Return true if the prefix exists
       return os.path.exists(self.getPath());
       
   def getWineVersion(self):
       return currentConfiguration = self.getConfigFile().getSetting("WINEVERSION")

   def getArch(self):
       return currentConfiguration = self.getConfigFile().getSetting("ARCH")
       
   @staticmethod
   def getList():
       prefixList = os.listdir(PREFIXES_PATH)
       prefixList.sort()
       return prefixList
   
             