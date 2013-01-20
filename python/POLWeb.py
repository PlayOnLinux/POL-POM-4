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

import threading, os, subprocess, time
from lib.Context import Context
from lib.Script import PrivateScript
import lib.playonlinux as playonlinux #FIXME

class POLWeb(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.context = Context()
        self.sendToStatusBarStr = ""
        self.sendAlertStr = None
        self.Gauge = False
        self.WebVersion = ""
        self.Show = False
        self.perc = -1
        self.updating = True
        
    def sendToStatusBar(self, message, gauge):
        self.sendToStatusBarStr = message
        self.Gauge = gauge
        self.Show = True

    def sendPercentage(self, n):
        self.perc = n

    def sendAlert(self, message):
        self.sendAlertStr = message

    def LastVersion(self):
        if(os.environ["POL_OS"] == "Mac"):
            fichier_online="version_mac"
        else:
            fichier_online="version2"
        return os.popen(os.environ["POL_WGET"]+' "'+os.environ["SITE"]+'/'+fichier_online+'.php?v='+os.environ["VERSION"]+'" -T 30 -O-','r').read()

    def real_check(self):
        self.WebVersion = self.LastVersion()

        if(self.WebVersion == ""):
            self.sendToStatusBar(_('{0} website is unavailable. Please check your connexion').format(os.environ["APPLICATION_TITLE"]), False)
        else:
            self.sendToStatusBar(_("Refreshing {0}").format(os.environ["APPLICATION_TITLE"]), True)
            self.updating = True
            bash_updater = PrivateScript("pol_update_list")

            p = bash_updater.runPoll()

            while(True):
                retcode = p.poll() 
                line = p.stdout.readline()
                try:
                    self.sendPercentage(int(line))
                except:
                    pass

                if(retcode is not None):
                    break
 
            self.updating = False
            if(playonlinux.VersionLower(os.environ["VERSION"],self.WebVersion)):
                self.sendToStatusBar(_('An updated version of {0} is available').format(os.environ["APPLICATION_TITLE"])+" ("+self.WebVersion+")",False)
                if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
                    self.sendAlert(_('An updated version of {0} is available').format(os.environ["APPLICATION_TITLE"])+" ("+self.WebVersion+")")
                os.environ["POL_UPTODATE"] = "FALSE"
            else:
                self.Show = False
                self.perc = -1
                os.environ["POL_UPTODATE"] = "TRUE"

        self.wantcheck = False

    def check(self):
        self.wantcheck = True

    def run(self):
        self.check()
        while(1):
            if(self.wantcheck == True):
                self.real_check()
            time.sleep(1)