#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from services.Environment import Environment

# Model
from models.PlayOnLinux import PlayOnLinux
from models.Script import PrivateScript
from models.Directory import *
from models.GuiServer import GuiServer
from models.ShortcutList import *

# Views
from views.MainWindow import MainWindow

class Controller(object):
   instance = None           
   def __init__(self, app):
      self.app = app
      self.playonlinux = PlayOnLinux()
      self.env = Environment()
      
      self.mainWindow()
    
   def mainWindow(self):
       self.mainWindow = MainWindow()
       self.app.SetTopWindow(self.mainWindow)
       self.mainWindow.Show(True)
       ShortcutFolder = Directory(self.env.getUserRoot()+"/shortcuts/")
       installedApps = ShortcutListFromFolder()
       ShortcutFolder.register(installedApps)
       installedApps.register(self.mainWindow.getAppList())
       
   def getPlayOnLinux(self):
       return self.playonlinux
         
   # Class content
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
       return self.playonlinux.getServer()
           
   def getServerQueue(self):
       return self.playonlinux.getServerQueue()
       
   def getServerState(self):
       return self.playonlinux.getState()
       
       
   # 
   def openFile(self, filename):
       openedFile = LocalFile(filename)
       openedFile.openCleverWay()
       
   # 
   def openUrl(self, url):
       self.urlHandler = PrivateScript("playonlinux-url_handler",[url])
       self.urlHandler.run()