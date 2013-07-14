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
from views.SetupWindow.Footer import *
       
class Step(object):
    def __init__(self, parent):
        self.collection = WidgetCollection()
        self.uiHelper = UIHelper()
        self.parent = parent
        self._returnMessage = None
        
        self.panel = wx.Panel(parent, -1, pos=(0,0), size=((520, 343 + self.uiHelper.addWindowMacOffset())))
        self.registerWidget(self.panel)
        
    def registerWidget(self, item):
        self.collection.append(item)
        
    def initStep(self):
        self.onInit()
        self._show()
        self.parent.getFooter().getNextButton().Enable(True)
        
        
    def leaveStep(self):   
        self._hide()
        self.parent.getFooter().getNextButton().Enable(False)

        
    ## Theses two methods are made to be overwritten
    # Abstract method
    def onInit(self):
        return
        
    # Abstract method
    def onNext(self):
        return

        
    def _hide(self):
        self.collection.hideAll()
        
    def _show(self):
        self.collection.showAll()

    # Setters
    def setNext(self, step):
        self.next = step
    
    def setReturnMessage(self, message):
        self._returnMessage = message
        
    # Getters
    def getReturnMessage(self):
        return self._returnMessage
        
        
class POL_SetupWindow_message(Step):
    def __init__(self, parent, message = "", title = ""):
        Step.__init__(self, parent)
        
        
        self.texte = wx.StaticText(self.panel, -1, message, pos=(20,80),size=(480,275),style=wx.ST_NO_AUTORESIZE)
        
        self.header = Header(self.panel, parent.getTopImage())
        self.header.setTitle(title)
        
        self.registerWidget(self.texte)
        self.registerWidget(self.header)
        
        self._hide()
        

class POL_SetupWindow_textbox(POL_SetupWindow_message):
    def __init__(self, parent, message = "", title = "", defaultValue = ""):
        POL_SetupWindow_message.__init__(self, parent, message, title)

        nSpace = message.count("\\n")+1
        self.textBox = wx.TextCtrl(self.panel, 400, "", size=(300,22), pos=(20,90+nSpace*16))
        self.textBox.SetValue(defaultValue)
        
        self.registerWidget(self.textBox)

    def onNext(self):
        self.setReturnMessage(self.textBox.GetValue())