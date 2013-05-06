#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

import webbrowser

from services.Environment import Environment
from services.ConfigService import ConfigService

# Model
from models.PlayOnLinux import PlayOnLinux
from models.Script import PrivateScript
from models.GuiServer import *
from models.Executable import Executable
from models.Directory import *
from models.ShortcutList import *
from models.PluginList import *
from models.Shortcut import *

# Views
from views.Question import Question

class Controller(object):
   def __init__(self):
      self.env = Environment()
      self.configService = ConfigService()
    
   def setApp(self, app):
      self.app = app
       
   def initPlayOnLinux(self):
      self._installedApps = ShortcutListFromUserFolder()
      self._installedApps.register(self.app.getMainWindow().getAppList())

      self._pluginList = PluginListFromUserFolder()
      self._pluginList.register(self.app.getMainWindow().getMenuBar())
      
   # Events
   def destroy(self):
       #try:
       #    self.getServer().closeServer()
       #except ErrServerIsNotRunning:
       #    pass
        
       # Destroy main window
       self.app.getMainWindow().Destroy()
              
       # Close all scripts
       for thread in threading.enumerate():
           if(isinstance(thread, Executable)):
               thread.__del__()
               
       # Destroy all timers
       for timer in Timer.getinstances():
           timer.stop()
       
       self.app.polDie()

       
       
   def donate(self):
        if(self.env.getOS() == "Mac"):
            webbrowser.open("http://www.playonmac.com/en/donate.html")
        else:
            webbrowser.open("http://www.playonlinux.com/en/donate.html")
    
   def runProgram(self, selectedProgram):
       _selectedProgram = Shortcut(selectedProgram)
       _shortcutName = _selectedProgram.getName()

       _selectedProgram.setDebug(False)
       
       try:
           _selectedProgram.run()
       except ErrPrefixDoesNotExist:
           Error(_("The virtual drive associated with {0} does not exists.").format(_shortcutName))
   
   def selectShortcut(self, panel, selectedProgram):
       _shortcut = Shortcut(selectedProgram)
       panel.generateContent(selectedProgram, _shortcut.hasManual(), _shortcut.getLinks(), _shortcut.getIcon())
       
       #panel.generateContent()

   def getInstalledApps(self):
       return self._installedApps.getStringArray()

   def getEnabledPlugins(self):
       return self._pluginList.getEnabledPlugins().getStringArray()
              
   """
       def RunDebug(self, event):
           
           if(selectedProgram.isDebug()):
               try:
                   self.debugFrame.analyseReal(0, game_prefix.getName())
                   self.debugFrame.Show()
                   self.debugFrame.SetFocus()
               except:
                   self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(Context().getAppName()),game_prefix.getName(),0)
                   self.debugFrame.Center(wx.BOTH)
                   self.debugFrame.Show()
           
           game_exec = self.getSelectedShortcut()
           playonlinux.SetDebugState(game_exec, True)
           self.Run(self, True)
   """       
                          
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