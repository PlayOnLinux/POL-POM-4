#!/usr/bin/python
# -*- coding:Utf-8 -*-

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



import wx, wx.animate, os, getopt, sys, urllib, signal, time, string, codecs, time, threading, socket
from subprocess import Popen,PIPE

from views.UIHelper import UIHelper
from views.SetupWindow.SetupWindow import SetupWindow

from services.Environment import *
from services.ConfigService import *

from patterns.Observer import Observer




class BashSetupWindow(SetupWindow): #fenêtre principale
    def __init__(self, controller, title, scriptPid, topImage, leftImage, isProtected):
        SetupWindow.__init__(self, controller, title, topImage, leftImage, isProtected)
        self.bashPid = scriptPid
        
    # Events
    def eventNext(self, event):
        SetupWindow.eventNext(self, event)
        if(self.currentStep.getReturnMessage() == None):
            self.unlockBash()
        else:
            self.sendAnswerToBash(self.currentStep.getReturnMessage())
        
    def eventCancel(self, event):
        if(self.protectedWindow == False):
            self.Destroy()
            time.sleep(0.1)
            self.controller.killScript(self.bashPid)
        else:
            wx.MessageBox(_("You cannot close this window").format(self.config.getAppName()),_("Error"))
    
    def unlockBash(self):
        self.controller.closeConnexion(self.bashPid)
    
    def sendAnswerToBash(self, data):
        self.controller.sendAnswerToBash(self.bashPid, data)
    