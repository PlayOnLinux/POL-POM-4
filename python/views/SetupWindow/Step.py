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

from services.Environment import Environment
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
        self._show()
        self.parent.getFooter().getNextButton().Enable(True)
        self.onInit()
        
        
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

    # Abstract method
    def update(self, *args):
        return None
        
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
        self.nSpace = message.count("\\n")+1
        
        self.header = Header(self.panel, parent.getTopImage())
        self.header.setTitle(title)
        
        self.registerWidget(self.texte)
        self.registerWidget(self.header)
        
        self._hide()
        

class POL_SetupWindow_textbox(POL_SetupWindow_message):
    def __init__(self, parent, message = "", title = "", defaultValue = ""):
        POL_SetupWindow_message.__init__(self, parent, message, title)

        self.textBox = wx.TextCtrl(self.panel, 400, "", size=(300,22), pos=(20,90+self.nSpace*16))
        self.textBox.SetValue(defaultValue)
        
        self.registerWidget(self.textBox)

    def onNext(self):
        self.setReturnMessage(self.textBox.GetValue())
        

class POL_SetupWindow_download(POL_SetupWindow_message):
     def __init__(self, parent, message = "", title = "", url = "", localDirectory = ""):
         POL_SetupWindow_message.__init__(self, parent, message, title)
         self.url = url
         self.localDirectory = localDirectory
         self.downloadGauge = DownloadGauge(self.panel, pos = (70,95+self.nSpace*16))
         self.txtEstimation = DownloadText(self.panel, pos = (20,135+self.nSpace*16))
         
         self.registerWidget(self.downloadGauge)
         self.registerWidget(self.txtEstimation)
         
     def getDownloadGauge(self):
         return self.downloadGauge
        
     def getDownloadText(self):
         return self.txtEstimation
     
     def getUrl(self):
         return self.url
     
     def getLocalDirectory(self):
         return self.localDirectory
         
     def onInit(self):
         self.parent.getController().startDownloadFromSetupWindowStep(self)
         
class POL_SetupWindow_wait(POL_SetupWindow_message):
     def __init__(self, parent, message = "", title = ""):
         POL_SetupWindow_message.__init__(self, parent, message, title)
         self.env = Environment()
         self.currentAngle = 1
         
         self.animation = wx.StaticBitmap(self.panel, -1, self.getLoaderFromAngle(self.currentAngle), (228,170))
         
         self.timer = wx.Timer(self.parent, 3)
         
         self.registerWidget(self.animation)
        
     def timerAnimation(self, event):
         self.currentAngle = ((self.currentAngle + 1) % 12)
         self.animation.SetBitmap(self.getLoaderFromAngle(self.currentAngle + 1))
                 
     def getLoaderFromAngle(self, angle):
         if(angle >= 1 and angle <= 12):
             image = wx.Image(self.env.getAppPath()+"/resources/images/setups/wait/"+str(angle)+".png")
         return image.ConvertToBitmap()
         
     def onInit(self):
         self.parent.releaseStep()
         self.parent.Bind(wx.EVT_TIMER, self.timerAnimation, self.timer)
         self.timer.Start(100)
    

class POL_SetupWindow_pulsebar(POL_SetupWindow_message):
     def __init__(self, parent, message = "", title = ""):
        POL_SetupWindow_message.__init__(self, parent, message, title)
       
        self.gauge = wx.Gauge(self.panel, -1, 50, size=(375, 18), pos = (70,95+self.nSpace*16))
        self.gaugeText = wx.StaticText(self.panel, -1, "",size=(480,30),style=wx.ST_NO_AUTORESIZE, pos=(20,135+self.nSpace*16))
        
        self.registerWidget(self.gauge)
        self.registerWidget(self.gaugeText)
        
     def onInit(self):
        self.parent.releaseStep()
             
     def update(self, *args):
        self.parent.releaseStep()
        command = args[0]
        data = args[1]
        
        if(command == "pulse"):
            try:
                data = float(data)/2
            except ValueError:
                data = 0
            
            self.gauge.SetValue(data)   
        
        if(command == "setText"):
            self.gaugeText.SetLabel(data)
             
"""
       # Other 
       setupWindowCommands = ["", "POL_SetupWindow_SetID", "POL_SetupWindow_UnsetID", 
       "POL_SetupWindow_shortcut_list", "POL_SetupWindow_prefix_selector", "POL_SetupWindow_pulsebar", "POL_SetupWindow_question", 
       "POL_SetupWindow_wait", "POL_SetupWindow_wait_bis", "POL_SetupWindow_free_presentation", "", 
       "POL_SetupWindow_debug", "POL_SetupWindow_textbox_multiline", "POL_SetupWindow_browse", "",
       "POL_SetupWindow_menu", "POL_SetupWindow_menu_num", "POL_SetupWindow_checkbox_list", "POL_SetupWindow_icon_menu", "POL_SetupWindow_licence", 
       "POL_SetupWindow_login", "POL_SetupWindow_file", "POL_SetupWindow_pulse", "POL_SetupWindow_set_text"]
"""