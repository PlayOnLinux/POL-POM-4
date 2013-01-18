#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

class ConfigFile()
   def __init__(self, filePath):
       self.configFile = filePath;
       
   def getSetting(self, setting):
      try:
         configFileContent = open(self.configFile,"r").readlines()
      except IOError as e:
         return("")

      i = 0
      line = ""
      while(i < len(configFileContent)):
         configFileContent[i] = configFileContent[i].replace("\n","")
         if(setting+"=" in configFileContent[i]):
            line = configFileContent[i]
            break
         i += 1
      try:
         line = string.split(line,"=")
         return(line[1])
      except:
         return("")
         

   def setSettings(setting, value):
      try:
         configFileContent = open(self.configFile,"r").readlines()
         fileExists = True
      except IOError as e:
         fileExists = False

      line = []
      found = False
       
      if(fileExists):
         # Try to overwrite the current setting
         i = 0
         while(i < len(configFileContent)):
            configFileContent[i] = configFileContent[i].replace("\n","")
            if(setting+"=" in configFileContent[i]):
               line.append(setting+"="+value)
               found = True
            else:
               line.append(configFileContent[i])
            i += 1
           
       # If the line is not found in the config file, we add it at the end
       if(found == False):
           line.append(setting+"="+value)

       # Now, we rewrite the config file
       configFileContent_write = open(self.configFile,"w")
       i = 0
       while(i < len(line)):
           configFileContent_write.write(line[i]+"\n")
           i+=1

   def DeleteSettings(setting):
      try:
         configFileContent = open(self.configFile,"r").readlines()
         fileExists = True
      except IOError as e:
         fileExists = False

      line = []
       
      if(fileExists):
         configFileContent = open(self.configFile,"r").readlines()
         i = 0
         while(i < len(configFileContent)):
            configFileContent[i] = configFileContent[i].replace("\n","")
            if(setting+"=" not in configFileContent[i]):
               line.append(configFileContent[i])
            i += 1

      configFileContent_write = open(self.configFile,"w")

      # Now, we rewrite the config file
      i = 0
      while(i < len(line)): 
          configFileContent_write.write(line[i]+"\n")
          i+=1
   