#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

import webbrowser, urlparse

from services.Environment import Environment
from services.ConfigService import ConfigService

# Model
from models.Script import PrivateScript
from models.Executable import Executable
from models.Directory import *
from models.ShortcutList import *
from models.PluginList import *
from models.Shortcut import *
from models.DistantFile import DistantFile

# Views
from views.Question import Question
from views.Modal import Modal
from views.SetupWindow import SetupWindow

# Other cntrollers
from controllers.GuiServer import *

class Controller(object):
   def __init__(self):
      self.env = Environment()
      self.configService = ConfigService()
      
      # Contains setupwindow list
      self.windowListFromPid = {}
      
      # Contains GuiServer clients listening
      self.clientListFromPid = {}
      
   def setApp(self, app):
      self.app = app
       
   def initPlayOnLinux(self):
      self._installedApps = ShortcutListFromUserFolder()
      self._installedApps.register(self.app.getMainWindow().getAppList())

      self._pluginList = PluginListFromUserFolder()
      self._pluginList.register(self.app.getMainWindow().getMenuBar())
      
      self._guiServer = GuiServer(self.app)
      self._guiServer.start()
      self._guiServer.waitForServer()
      
      events.EVT_GUISERVER(self.app, self.eventGuiServer)

   # Manage GUI Server
   def sendAnswerToBash(self, pid, data):
       self.clientListFromPid[pid].sendData(data)
       self.closeConnexion(pid)
       
   def closeConnexion(self, pid):
       self.clientListFromPid[pid].unlock()
       del self.clientListFromPid[pid]
       
   def eventGuiServer(self, event):
       data = event.data
       command = data[0]
       scriptPid = data[1]
       
       self.clientListFromPid[scriptPid] = event.client
       
       if(command == "SimpleMessage"):
           Modal(data[2])
           self.closeConnexion(scriptPid)
           
       if(command == "POL_Die"):
           playOnLinuxApppolDie()
           self.closeConnexion(scriptPid)    
       
       if(command == "POL_Restart"):
           playOnLinuxApp.polRestart()
           self.closeConnexion(scriptPid)  
       
       if(command == 'POL_SetupWindow_Init'):
          if(len(data) == 6):
               isProtected = (data[5] == "TRUE") 
               setupWindow =  SetupWindow(self, title = data[2], scriptPid = scriptPid, topImage = data[3], leftImage = data[4], isProtected = isProtected)
               self.windowListFromPid[scriptPid] = setupWindow
               self.closeConnexion(scriptPid)
       
       if(command == 'POL_SetupWindow_Close'):
           try:
               self.windowListFromPid[scriptPid].Destroy()
               self.closeConnexion(scriptPid)
           except KeyError:
               print "Please use POL_SetupWindow_Init first"
          
       
       # Other 
       setupWindowCommands = ["POL_SetupWindow_message", "POL_SetupWindow_SetID", "POL_SetupWindow_UnsetID", 
       "POL_SetupWindow_shortcut_list", "POL_SetupWindow_prefix_selector", "POL_SetupWindow_pulsebar", "POL_SetupWindow_question", 
       "POL_SetupWindow_wait", "POL_SetupWindow_wait_bis", "POL_SetupWindow_free_presentation", "POL_SetupWindow_textbox", 
       "POL_SetupWindow_debug", "POL_SetupWindow_textbox_multiline", "POL_SetupWindow_browse", "POL_SetupWindow_download",
       "POL_SetupWindow_menu", "POL_SetupWindow_menu_num", "POL_SetupWindow_checkbox_list", "POL_SetupWindow_icon_menu", "POL_SetupWindow_licence", 
       "POL_SetupWindow_login", "POL_SetupWindow_file", "POL_SetupWindow_pulse", "POL_SetupWindow_set_text"]
       
       if(command in setupWindowCommands):        
           arguments = data[2:]       
           try:
               setupWindowObject = self.windowListFromPid[scriptPid]
           except KeyError:
               print "Err. Please use POL_SetupWindow_Init first"
               self.closeConnexion(scriptPid)
           else: 
               try:
                   setupWindowFunction = getattr(setupWindowObject, command)
               except AttributeError:
                   Error ('Function not found "%s" (%s)' % (command, arguments) )
               else:
                   try:
                       setupWindowFunction(*arguments)
                       
                       if(command == "POL_SetupWindow_download"):
                           # Download parameters
                           url = arguments[2]
                           localDirectory = arguments[3]
                           chemin = urlparse.urlsplit(url)[2]
                           nomFichier = chemin.split('/')[-1]
                           local = localDirectory + nomFichier
                           
                           # Distant file object
                           # We register the observer
                           distantFile = DistantFile(url)
                           distantFile.register(setupWindowObject.getDownloadGauge())
                           distantFile.register(setupWindowObject.getDownloadText())
                           
                           distantFile.download(local)
                       
                   except TypeError, e:
                       print 'Error: %s (%s)' % (e, arguments)
                       
       
         
   # Events
   def destroy(self):
       try:
           self._guiServer.closeServer()
       except ErrServerIsNotRunning:
           pass
       
       # Destroy setupwindow
       for pid in self.windowListFromPid:
           self.windowListFromPid[pid].Destroy()
            
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


       
   # Manage events
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

   def startPlayOnLinuxConsole(self):
       _polshell = PrivateScript("POLShell")
       _polshell.linkToServer(self._guiServer)
       _polshell.start()

   # Get data from models
   def getInstalledApps(self):
       return self._installedApps.getStringArray()

   def getEnabledPlugins(self):
       enabledPlugins = self._pluginList.getEnabledPlugins()
       return enabledPlugins.getNameAndIconArray()
       
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
         
           
           
   # Pour le moment on sait pas trop ca                 
   def appStartupBeforeServer(self):
       startupScript = PrivateScript("startup")
       startupScript.start()
       startupScript.waitProcessEnd()
       SystemCheck().doFullCheck()
       
   def appStartupAfterServer(self):
       startupScript = PrivateScript("startup_after_server")
       startupScript.start()
          
       
   # 
   def openFile(self, filename):
       openedFile = LocalFile(filename)
       openedFile.openCleverWay()
       
   # 
   def openUrl(self, url):
       self.urlHandler = PrivateScript("playonlinux-url_handler",[url])
       self.urlHandler.run()