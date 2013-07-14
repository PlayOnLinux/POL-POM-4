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

from services.Environment import *
from services.ConfigService import *

from patterns.Observer import Observer


class Footer(wx.Panel):
    def __init__(self, parent):
        self._uiHelper = UIHelper()
        wx.Panel.__init__(self, parent, -1, size=(522,45), pos=(-1,358), style = self._uiHelper.widgetBorders())
        self._cancelButton = wx.Button(self, wx.ID_CANCEL, _("Cancel"), pos=(425,0),size=(85,self._uiHelper.getSetupWindowButtonHeight()))
        self._nextButton = wx.Button(self, wx.ID_FORWARD, _("Next"), pos=(335,0),size=(85,self._uiHelper.getSetupWindowButtonHeight()))
        
        self._cancelButton.Enable(not parent.isProtectedWindow())
        
    def getNextButton(self):
        return self._nextButton