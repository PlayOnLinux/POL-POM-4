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

# PlayOnLinux imports
from lib.Environement import Environement
from lib.Context import Context
from lib.SystemManager import SystemManager
from lib.SystemCheck import SystemCheck
from lib.Script import PrivateScript
from lib.ConfigFile import UserConfigFile
from lib.File import File
from lib.GuiServer import GuiServer
from lib.UI import UI


# Views
from views.MainWindow import MainWindow



class PlayOnLinuxApp(wx.App):
    def OnInit(self):

        Environement().createContext()
        self.initLanguage()
        self.playonlinuxSettings = UserConfigFile()
        
        
        PrivateScript("startup").run()
        SystemCheck().doFullCheck()
        
        # Anonymous reports ?
        self.askForReports()
        
        # Open documents opened with POL
        self.openDocuments() 
        

        self.SetClassName(Context().getAppName())
        self.SetAppName(Context().getAppName())
        self.frame = MainWindow(None, -1, Context().getAppName())
        
        # Gui Server
        self.initPOLServer()
        
        
        PrivateScript("startup_after_server").runBackground()
   
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        
        # Catch CTRL+C
        signal.signal(signal.SIGINT, self.CatchCtrlC)
        
        return True

    def openDocuments(self):
        for f in  sys.argv[1:]:
            self.MacOpenFile(f)
            
    def initPOLServer(self):
        self.POLServer = GuiServer()
        self.POLServer.setMainWindow(self.frame)
        self.POLServer.start()
        self.POLServer.waitForServer()
        return self.POLServer
        
    def askForReports(self):
        if(not Context().isDebianPackage()):
            if(self.playonlinuxSettings.getSetting("SEND_REPORT") == ""):
                if(wx.YES == wx.MessageBox(_('Do you want to help {0} to make a compatibility database?\n\nIf you click yes, the following things will be sent to us anonymously the first time you run a Windows program:\n\n- You graphic card model\n- Your OS version\n- If graphic drivers are installed or not.\n\n\nThese information will be very precious for us to help people.').format(Context().getAppName()).decode("utf-8","replace"), Context().getAppName(),style=wx.YES_NO | wx.ICON_QUESTION)):
                    self.playonlinuxSettings.setSetting("SEND_REPORT","TRUE")
                else:
                    self.playonlinuxSettings.setSetting("SEND_REPORT","FALSE")
                    
    def BringWindowToFront(self):
        # FIXME
        try: # it's possible for this event to come when the frame is closed
            self.GetTopWindow().Raise()
        except:
            pass

    def MacOpenFile(self, filename):
        openedFile = File(filename)
        openedFile.openCleverWay()

    def MacOpenURL(self, url):
        if(Context().getOS() == "Mac" and "playonlinux://" in url):
            wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnLinux"), Context().getAppName())
        if(Context().getOS() == "Linux" and "playonmac://" in url):
            wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnMac"), Context().getAppName())

        PrivateScript("playonlinux-url_handler",[url]).runPoll()

    def MacReopenApp(self):
        self.BringWindowToFront()

    def CatchCtrlC(self, signal, event): # Catch SIGINT
        print "\nCtrl+C pressed. Killing all processes..."
        SystemManager().polDie()
        
    def initLanguage(self):
        if(Context().isDebianPackage()):
            languages = os.listdir('/usr/share/locale')
        else:
            languages = os.listdir(Context().getAppPath()+'/lang/locale')

        langid = wx.LANGUAGE_DEFAULT
        if(Context().isDebianPackage()):
            localedir = "/usr/share/locale"
        else:
            localedir = os.path.join(Context().getAppPath(), "lang/locale")

        domain = "pol"
        mylocale = wx.Locale(langid)
        mylocale.AddCatalogLookupPathPrefix(localedir)
        mylocale.AddCatalog(domain)

        mytranslation = gettext.translation(domain, localedir, [mylocale.GetCanonicalName()], fallback = True)
        mytranslation.install()
        
app = PlayOnLinuxApp(redirect=False)
app.MainLoop()