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
from views.widgets.DownloadGauge import DownloadGauge
from views.widgets.DownloadText import DownloadText
from views.SetupWindow.Title import Title
from views.SetupWindow.Text import Text

from services.Environment import *
from services.ConfigService import *

from patterns.Observer import Observer


class Header(wx.Panel):
    def __init__(self, panel, topImage):
        self.config = ConfigService()
        self.uiHelper = UIHelper()
        
        wx.Panel.__init__(self, panel, -1, style = self.uiHelper.widgetBorders(), size=(522,65))
        self.SetBackgroundColour((255,255,255))

        # Images
        if(os.path.exists(topImage)):
            self.topImage = self.uiHelper.getBitmap(topImage)
        else:
            self.topImage = self.uiHelper.getBitmap("setups/default/top.png")
        
        self.topImageWidget = wx.StaticBitmap(self, -1, self.topImage, (520 - self.topImage.GetWidth() , 0), wx.DefaultSize)        

        #Text
        self.titreHeader = Title(self,  _('{0} Wizard').format(self.config.getAppName()), pos=(5,5), size=(340,356))
        
        self.stepTitle = Text(self, "", pos=(20,30), size=(340,356))
        self.stepTitle.SetForegroundColour((0,0,0)) # For dark themes
        
    def setTitle(self, title):
        self.stepTitle.SetLabel(title)
        
    def Destroy(self):
        self.titreHeader.Destroy()
        self.topImageWidget.Destroy()
        wx.Panel.Destroy(self)   
