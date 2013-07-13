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

from services.Environment import *
from services.ConfigService import *
        
        
from views.UIHelper import UIHelper

# SetupWindow
from views.SetupWindow.WidgetCollection import *
from views.SetupWindow.Header import *


class Step(object):
    def __init__(self):
        self.next = None
        self.collection = WidgetCollection()
        self.currentStep = False
        self.uiHelper = UIHelper()
        
    def registerWidget(self, item):
        self.collection.append(item)
        
    def eventNext(self, event):
        self.leaveStep()
    
    def initStep(self):
        self.onInit()
        self.show()
        self.currentStep = True
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.eventNext)
    
    def leaveStep(self):
        self.onNext()
        self.hide()
        self.currentStep = False
        
    ## Theses two methods are made to be overwritten
    # Abstract method
    def onInit(self):
        return
        
    # Abstract method
    def onNext(self):
        return

        
    def hide(self):
        self.collection.hideAll()
        
    def show(self):
        self.collection.showAll()

    # Setters
    def setNext(self, step):
        self.next = step
        
class POL_SetupWindow_message(Step):
    def __init__(self, parent, title = "", text = ""):
        Step.__init__(self)
        
        panel = wx.Panel(parent, -1, pos=(0,0), size=((520, 398 + self.uiHelper.addWindowMacOffset())))
        
        self.texte = wx.StaticText(panel, -1, text, pos=(20,80),size=(480,275),style=wx.ST_NO_AUTORESIZE)
        self.registerWidget(self.texte)
        
        self.header = Header(panel, parent.getTopImage())
        self.header.setTitle(title)
        self.registerWidget(self.header)
        
        