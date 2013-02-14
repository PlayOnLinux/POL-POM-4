#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2008 Pâris Quentin

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

# PlayOnLinux wrapper
encoding = 'utf-8'

import os, getopt, sys, urllib, signal, string, time, webbrowser, gettext, locale, sys, shutil, subprocess, signal

try :
    os.environ["POL_OS"]
except :
    print "ERROR ! Please define POL_OS environment var first."
    os._exit(1)

if(os.environ["POL_OS"] == "Linux"):
    import wxversion
    wxversion.ensureMinimal('2.8')

import wx
import lib.lng as lng
import lib.playonlinux as playonlinux, lib.Variables as Variables
import guiv3 as gui, install, options, wine_versions as wver, sp, configure, threading, debug, gui_server



class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):

        wx.Frame.__init__(self, parent, 1000, title, size = (0,0), style=wx.NO_BORDER|wx.WS_EX_BLOCK_EVENTS|wx.FRAME_NO_TASKBAR|wx.FRAME_SHAPED) # I know, that's not clean at all
        self.windowList = {}
        self.registeredPid = []
        self.myScript = None

        # Manage updater
        # SetupWindow timer. The server is in another thread and GUI must be run from the main thread
        self.SetupWindowTimer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.SetupWindowAction, self.SetupWindowTimer)
        self.SetupWindowTimer_action = None
        self.SetupWindowTimer.Start(10)
        self.SetupWindowTimer_delay = 10
        self.windowOpened = 0

    def SetupWindowTimer_SendToGui(self, recvData):
        recvData = recvData.split("\t")
        while(self.SetupWindowTimer_action != None):
            time.sleep(0.1)
        self.SetupWindowTimer_action = recvData
        
    def SetupWindowAction(self, event):
        if(self.SetupWindowTimer_action != None):
            return gui_server.readAction(self)
        if(self.myScript.programrunning == False):
            self.POLDie()


    def POLDie(self):
        for pid in self.registeredPid:
            os.system("kill -9 -%d 2> /dev/null" % pid)
            os.system("kill -9 %d 2> /dev/null" % pid) 
        app.POLServer.closeServer()
        os._exit(0)

    def POLRestart(self):
        return False

    def ForceClose(self, signal, frame): # Catch SIGINT
        print "\nCtrl+C pressed. Killing all processes..."
        self.POLDie()

   
class Program(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)
                self.start()
                self.programrunning = True

        def run(self):
                self.running = True
                self.chaine = ""
                print "Script started "+sys.argv[1]
                for arg in sys.argv[2:]:
                        self.chaine+=" \""+arg+"\""
                self.proc = subprocess.Popen("bash \""+sys.argv[1]+"\""+self.chaine, shell=True)
                while(self.running == True):
                        self.proc.poll()
                        if(self.proc.returncode != None):
                            self.programrunning = False
                        time.sleep(1)

class PlayOnLinuxApp(wx.App):
    def OnInit(self):
        lng.iLang()

        os.system("bash "+Variables.playonlinux_env+"/bash/startup")

        self.frame = MainWindow(None, -1, os.environ["APPLICATION_TITLE"])
        # Gui Server
        self.POLServer = gui_server.gui_server(self.frame)
        self.POLServer.start()
        
        i = 0
        while(os.environ["POL_PORT"] == "0"):
            time.sleep(0.01)
            if(i >= 300):
                 wx.MessageBox(_("{0} is not able to start POL_SetupWindow_server.").format(os.environ["APPLICATION_TITLE"]),_("Error"))
                 os._exit(0)
                 break
            i+=1 
        self.frame.myScript = Program()
   
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        self.frame.Hide()
        return True
  

lng.Lang()

app = PlayOnLinuxApp(redirect=False)
app.MainLoop()
