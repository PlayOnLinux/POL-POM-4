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
from lib.Context import Context
from lib.SystemCheck import SystemCheck
from lib.Script import PrivateScript
from lib.ConfigFile import GlobalConfigFile
from lib.File import File


# Views
from views.MainWindow import MainWindow

import gui_server




class PlayOnLinuxApp(wx.App):
    def OnInit(self):
        
        # Create a context
        self.context = Context()
        self.context.initLanguage()
        
        self.playonlinuxSettings = GlobalConfigFile(self.context)
        
        PrivateScript(self.context, "startup").run()
        SystemCheck(self.context).doFullCheck()
        
        
        close = False
        exe_present = False
        
        for f in  sys.argv[1:]:
            self.MacOpenFile(f)
            if(".exe" in f or ".EXE" in f):
                exe_present = True
            close = True

        if(close == True and exe_present == False):
            os._exit(0)

        

        self.SetClassName(self.context.getAppName())
        self.SetAppName(self.context.getAppName())
        self.frame = MainWindow(self.context, None, -1, self.context.getAppName())
        
        # Gui Server
        self.context.initPOLServer(self.frame)
        
        PrivateScript(self.context, "startup_after_server").runPoll()
   
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        
        return True

    def askForReports(self):
        if(not self.context.isDebianPackage()):
            if(self.playonlinuxSettings.getSetting("SEND_REPORT") == ""):
                if(wx.YES == wx.MessageBox(_('Do you want to help {0} to make a compatibility database?\n\nIf you click yes, the following things will be sent to us anonymously the first time you run a Windows program:\n\n- You graphic card model\n- Your OS version\n- If graphic drivers are installed or not.\n\n\nThese information will be very precious for us to help people.').format(self.context.getAppName()).decode("utf-8","replace"), self.context.getAppName(),style=wx.YES_NO | wx.ICON_QUESTION)):
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
        draggedFile = File(filename)
        draggedFile.openCleverWay()

    def MacOpenURL(self, url):
        if(os.environ["POL_OS"] == "Mac" and "playonlinux://" in url):
            wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnLinux"), self.context.getAppName())
        if(os.environ["POL_OS"] == "Linux" and "playonmac://" in url):
            wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnMac"), self.context.getAppName())

        os.system("bash \"$PLAYONLINUX/bash/playonlinux-url_handler\" \""+url+"\" &")

    def MacReopenApp(self):
        self.BringWindowToFront()


app = PlayOnLinuxApp(redirect=False)
app.MainLoop()