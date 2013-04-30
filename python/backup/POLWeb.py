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
encoding = 'utf-8'

import threading, os, subprocess, time, wx

from lib.Script import POLUpdaterScript
from lib.Context import Context
from lib.Downloader import Downloader
from lib.Environement import Environement
from lib.SystemManager import SystemManager


class POLWeb(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.context = Context()
        self.systemManager = SystemManager()
        
        self.sendToStatusBarStr = ""
        self.sendAlertStr = None
        self.Gauge = False
        self.WebVersion = ""
        self.Show = False
        self.perc = -1
        self.updating = True
        
    def sendToStatusBar(self, message, showGauge):
        self.sendToStatusBarStr = message
        self.Gauge = showGauge
        self.Show = True

    def sendPercentage(self, n):
        self.perc = n

    def sendAlert(self, message):
        self.sendAlertStr = message

    def getAlert(self):
        alert = self.sendAlertStr
        self.sendAlertStr = None
        return alert
        
    def LastVersion(self):
        
        if(self.context.getOS() == "Mac"):
            fichier_online="version_mac"
        else:
            fichier_online="version2"
        
        url = Environement().getSetting("SITE")+"/"+fichier_online+".php?v="+Context().getAppVersion()

        latestVersionDownload = Downloader(url, "/tmp/test") #FIXME
        latestVersionDownload.start()
        currentVersion = latestVersionDownload.getContent()
        return currentVersion

    def real_check(self):
        self.WebVersion = self.LastVersion()

        if(self.WebVersion == None):
            self.sendToStatusBar(_('{0} website is unavailable. Please check your connexion').format(Context().getAppName()), False)
        else:
            self.sendToStatusBar(_("Refreshing {0}").format(Context().getAppName()), True)
            self.updating = True
            bashUpdater = POLUpdaterScript(self)
            bashUpdater.start()
            bashUpdater.waitProcessEnd()
            self.updating = False

            # FIXME
            #if(playonlinux.VersionLower(os.environ["VERSION"],self.WebVersion)):
                #self.sendToStatusBar(_('An updated version of {0} is available').format(os.environ["APPLICATION_TITLE"])+" ("+self.WebVersion+")",False)
                #if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
                #    self.sendAlert(_('An updated version of {0} is available').format(os.environ["APPLICATION_TITLE"])+" ("+self.WebVersion+")")
                #os.environ["POL_UPTODATE"] = "FALSE"
            #else:
                #self.Show = False
                #self.perc = -1
                #os.environ["POL_UPTODATE"] = "TRUE"

        self.wantcheck = False

    def check(self):
        self.wantcheck = True

    def run(self):
        self.check()
        while(True and not wx.GetApp().isExiting()):
            if(self.wantcheck == True):
                self.real_check()
            time.sleep(1)