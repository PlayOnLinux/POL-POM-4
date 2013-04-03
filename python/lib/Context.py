#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

import os, random, sys, string, gettext, locale
import wx, wxversion


# Singleton
class Context(object):
   instance = None    
   
   def __new__(myClass):
       if(myClass.instance is None):
           myClass.instance = object.__new__(myClass)
       return myClass.instance
       
   def __init__(self):
      try: 
          self.alreadyInit
      except AttributeError:
          self.alreadyInit = True
          
          self.registeredPid = [] # List of bash pids belonging to POL 
          self.windowOpened = 0   # Number of POL_SetupWindow opened   
          self.created = False    # The context is initialized, but not created

   def isCreated(self):
       return self.created

   def setCreated(self):
       self.created = True
       
   # Getters and setters
   
   # PlayOnLinux OS (Linux or Mac)
   def getOS(self):
       return self.pol_os
         
   def setOS(self, os):
       self.pol_os = os
   
   def getCodeName(self):
       if(self.getOS == "Linux"):
           return "linux"
       if(self.getOS == "Mac"):
           return "darwin"
         
   # App path 
   def getAppPath(self):
      return self.appPath
         
   def setAppPath(self, path):
      self.appPath = path
         
   # User root
   def getUserRoot(self):
       return self.userRoot
      
   def setUserRoot(self, path):
       self.userRoot = path
         
   # 64 bits
   def is64bit(self):
       return self.is64
   
   def set64bit(self, isit):
       self.is64 = isit;

   
   # Application name (Exemple : PlayOnLinux)
   def getAppName(self):
       return self.appName
       
   def setAppName(self, title):
       self.appName = title 
       
   def getAppVersion(self):
       return self.appVersion
 
   def setAppVersion(self, version):
       self.appVersion = version
   
   def setDebianPackage(self, value):
       self.isDebian = value
       
   def isDebianPackage(self):
       return self.isDebian
       
   def getRegisteredPids(self):
       return self.registeredPid
      
   def getWindowOpened(self):
       return self.windowOpened
      
   def incWindowOpened(self):
       self.windowOpened += 1
   
   def decWindowOpened(self):
       self.windowOpened -= 1  

   def registerPid(self, pid):
       self.registeredPid.append(pid)
       
   def setUpToDate(self, value):
       self.upToDate = value
       
   def isUpToDate(self):
       try:
           return self.upToDate
       except AttributeError:
           return True