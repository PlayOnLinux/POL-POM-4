#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from services.Environment import Environment
from services.ConfigService import ConfigService

# Model
from models.PlayOnLinux import PlayOnLinux
from models.Script import PrivateScript
from models.GuiServer import *
from models.Executable import Executable
from models.Directory import *
from models.ShortcutList import *

# Views
from views.Question import Question

class Controller(object):
   instance = None           
   def __init__(self, app):
      self.app = app
      self.env = Environment()
      self.configService = ConfigService()
      
      self.server = GuiServer()
      self.playonlinux = PlayOnLinux()
      
      self._shortcutFolder = Directory(self.env.getUserRoot()+"/shortcuts/")
      self._installedApps = ShortcutListFromFolder()
      self._shortcutFolder.register(self._installedApps)
      self._installedApps.register(self.app.getMainWindow().getAppList())
    

      self.registerEvents()
      
   def registerEvents(self):
       wx.EVT_CLOSE(self.app.getMainWindow(), self.eventClosePol)
       wx.EVT_MENU(self.app.getMainWindow(),  wx.ID_EXIT,  self.eventClosePol)
       
       
   # Events
   def eventClosePol(self, event):
       if(self.configService.getSetting("DONT_ASK_BEFORE_CLOSING") == "TRUE" or Question(_('Are you sure you want to close all [APP] Windows?')).getAnswer()):
           try:
               self.getServer().closeServer()
           except ErrServerIsNotRunning:
               pass
            
           # Destroy main window
           self.app.getMainWindow().Destroy()
           
           # Destroy models
           self._shortcutFolder.destroy()
                      
           # Close all scripts
           for thread in threading.enumerate():
               if(isinstance(thread, Executable)):
                   thread.__del__()
           
           
           self.app.polDie()
           
   def appStartupBeforeServer(self):
       startupScript = PrivateScript("startup")
       startupScript.start()
       startupScript.waitProcessEnd()
       SystemCheck().doFullCheck()
       
   def appStartupAfterServer(self):
       startupScript = PrivateScript("startup_after_server")
       startupScript.start()
       
   # Server managing
   def getServer(self):
       return self.server
           
   def getServerQueue(self):
       return self.getServer().getQueue()
       
   def getServerState(self):
       return self.getServer().getState()
       
   
       
   # 
   def openFile(self, filename):
       openedFile = LocalFile(filename)
       openedFile.openCleverWay()
       
   # 
   def openUrl(self, url):
       self.urlHandler = PrivateScript("playonlinux-url_handler",[url])
       self.urlHandler.run()