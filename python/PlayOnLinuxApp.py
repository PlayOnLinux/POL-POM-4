#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Pâris Quentin

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
encoding = 'utf-8'

# Python imports
import os, getopt, sys, urllib, signal, string, time, webbrowser, gettext, locale, sys, shutil, subprocess, signal, threading
import wx, wx.aui
import sys, traceback, threading

# PlayOnLinux imports
from controllers.Controller import *
from services.ConfigService import *

# Views
from views.MainWindow import MainWindow
from views.Question import Question
from views.Message import Message


class PlayOnLinuxApp(wx.App):
    def OnInit(self):
        self.controller = Controller()        
        self.initLanguage()    
        self.controller.appStartupBeforeServer()
        
        # Anonymous reports ?
        self.askForReports()
        
        # Open documents opened with POL
        self.openDocuments() 

        # Init main frame
        self.SetClassName(self.playonlinux.getAppName())
        self.SetAppName(self.playonlinux.getAppName())
        self.frame = MainWindow(None, -1, self.playonlinux.getAppName())
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        
        # Gui Server
        self.initPOLServer()
        
        # Startup Script after servr
        self.controller.appStartupAfterServer()
        
        # Catch CTRL+C
        signal.signal(signal.SIGINT, self.CatchCtrlC)
        
        # Exiting
        self.exiting = False
        return True

    def openDocuments(self):
        for f in  sys.argv[1:]:
            self.MacOpenFile(f)
            
    def initPOLServer(self):
        POLServer = self.controller.getServer()
        POLServer.start()
        POLServer.waitForServer()
        return POLServer
        
    def askForReports(self):
        if(not self.controller.getPlayOnLinux().isDebianPackage()):
            if(self.controller.getSetting("SEND_REPORT") == ""):
                if(Question(_('Do you want to help [APP] to make a compatibility database?\n\nIf you click yes, the following things will be sent to us anonymously the first time you run a Windows program:\n\n- You graphic card model\n- Your OS version\n- If graphic drivers are installed or not.\n\n\nThese information will be very precious for us to help people.'))):
                    self.controller.setSetting("SEND_REPORT","TRUE")
                else:
                    self.controller.setSetting("SEND_REPORT","FALSE")
                    
    def BringWindowToFront(self):
        self.GetTopWindow().Raise()
       
    def MacOpenFile(self, filename):
        self.controller.openFile(filename)

    def MacOpenURL(self, url):
        if(self.controller.getEnv().getOS() == "Mac" and "playonlinux://" in url):
            Message(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnLinux"))
        if(self.controller.getEnv().getOS() == "Linux" and "playonmac://" in url):
            Message(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnMac"))

        self.controller.openUrl(url)

    def MacReopenApp(self):
        self.BringWindowToFront()

    def CatchCtrlC(self, signal, event): # Catch SIGINT
        print "\nCtrl+C pressed. Killing all processes..."
        self.polDie()
        
    def initLanguage(self):
        if(self.controller.getPlayOnLinux().isDebianPackage()):
            languages = os.listdir('/usr/share/locale')
            localedir = "/usr/share/locale"
        else:
            languages = os.listdir(self.controller.getPlayOnLinuxEnv().getAppPath()+'/lang/locale')
            localedir = os.path.join(self.controller.getPlayOnLinuxEnv().getAppPath(), "lang/locale")        

        domain = "pol"
        mylocale = wx.Locale(wx.LANGUAGE_DEFAULT)
        mylocale.AddCatalogLookupPathPrefix(localedir)
        mylocale.AddCatalog(domain)

        mytranslation = gettext.translation(domain, localedir, [mylocale.GetCanonicalName()], fallback = True)
        mytranslation.install()
        
      
    # Manage PlayOnLinux Exit
    def isExiting(self):
        try:
            return self.exiting
        except AttributeError: #self.exiting is not existing yet, the application has just been launched
            return False
            
    # Should not be used.
    def hardExit(self, code = 0):
        os._exit(code)
   
    def softExit(self, code = 0):
        self.exiting = True
        # Close GUI Server
        try:
            self.controller.getServer().closeServer()
        except ErrServerIsNotRunning:
            pass
            
        # Destroy main window
        try:
            self.frame.Destroy()
        except AttributeError: # The frame does not exist yet
            pass
            
        # Close all scripts
        for thread in threading.enumerate():
            if(isinstance(thread, Executable)):
                thread.__del__()
            
        return code
        
    def polDie(self):
        self.softExit(0)
        
    def polReset(self):
        self.softExit(63)
    
    
playOnLinuxApp = PlayOnLinuxApp(redirect=False)
playOnLinuxApp.MainLoop()