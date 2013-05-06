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
from models.Shortcut import *

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
      self._iconsFolder = Directory(self.env.getUserRoot()+"/icones/full_size/")
      
      self._installedApps = ShortcutListFromFolder()
      
      # Installed apps observes two folders
      self._shortcutFolder.register(self._installedApps)
      self._iconsFolder.register(self._installedApps)
      
      self._installedApps.register(self.app.getMainWindow().getAppList())

      self.registerEvents()
      
   def registerEvents(self):
       ### Main window events
       ## Closing events
       wx.EVT_CLOSE(self.app.getMainWindow(), self.eventClosePol)
       wx.EVT_MENU(self.app.getMainWindow(),  wx.ID_EXIT,  self.eventClosePol)
       
       ## Run a program
       # Double click on the list
       wx.EVT_TREE_ITEM_ACTIVATED(self.app.getMainWindow(), 105, self.eventRunProgram) 
       # Toolbar button
       wx.EVT_MENU(self.app.getMainWindow(), wx.ID_OPEN,  self.eventRunProgram)
       
       ## Menu events
       wx.EVT_MENU(self.app.getMainWindow(), 216,  self.eventDonate)
       
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
           self._iconsFolder.destroy()
            
           # Close all scripts
           for thread in threading.enumerate():
               if(isinstance(thread, Executable)):
                   thread.__del__()
           
           
           self.app.polDie()

   def eventDonate(self, event):
        if(self.env.getOS() == "Mac"):
            webbrowser.open("http://www.playonmac.com/en/donate.html")
        else:
            webbrowser.open("http://www.playonlinux.com/en/donate.html")
    
   def eventRunProgram(self, event):
       selectedProgram = Shortcut(self.app.getMainWindow().getAppList().getSelectedShortcut())
       shortcutName = selectedProgram.getName()

       selectedProgram.setDebug(False)
       
       try:
           selectedProgram.run()
       except ErrPrefixDoesNotExist:
           Error(_("The virtual drive associated with {0} does not exists.").format(shortcutName))
       
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