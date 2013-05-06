#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, os, wx

from models.Observable import *
from models.Observer import *
from models.Plugin import Plugin
from models.Directory import Directory

from services.Environment import Environment
from services.ConfigService import ConfigService

class PluginList(Observer, Observable):
   def __init__(self, pluginList = []):
       Observable.__init__(self)
       Observer.__init__(self)
       self.pluginList = pluginList[:]
       self.env = Environment()
       
   def getEnabledPlugins(self):
       result = []
       for plugin in self.pluginList:
           if(plugin.isEnabled()):
               result.append(plugin)
       return PluginList(result)
       
   def getStringArray(self):
       result = []
       for item in self.pluginList:
           result.append(item.getName())
       return result

   def getNameAndIconArray(self):
       result = []
       for item in self.pluginList:
           name = item.getName()
           icon = self.env.getUserRoot()+"/plugins/"+name+"/icon"
           if(not os.path.exists(icon)):
              icon = self.configService.getAppPath()+"/resources/icons/playonlinux16.png"
           result.append((name, icon))
           
       return result
       
   def getList(self):
       return self.pluginList
       
class PluginListFromUserFolder(PluginList):  
   def __init__(self):
       PluginList.__init__(self)
       self.env = Environment()
       self._pluginFolder = Directory(self.env.getUserRoot()+"/plugins/")
       self._pluginFolder.checkForChange()
       self._pluginFolder.register(self)
              
   def notify(self):
       pluginList = []   
       for ndx, member in enumerate(self._pluginFolder):
           pluginList.append(Plugin(member))
       self.pluginList = pluginList
       self.update()