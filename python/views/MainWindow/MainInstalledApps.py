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

# Python imports
import os, getopt, sys, urllib, string, time, webbrowser, gettext, locale, sys, shutil, subprocess, threading
import wx, wx.aui


from services.ConfigService import ConfigService
from services.Environment import Environment

from patterns.Observer import Observer
from patterns.Observable import Observable

from views.ShortcutIcon import ShortcutIcon
from views.UIHelper import UIHelper
from views.InstalledApps import InstalledApps

class MainInstalledApps(InstalledApps):
    def __init__(self, frame, controller):
        InstalledApps.__init__(self, frame, controller, style = wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        self.uiHelper = UIHelper()
        self.playonlinuxSettings = ConfigService()
        self.iconSize = self.playonlinuxSettings.getIntSetting("ICON_SIZE", default = 32)
        
    def setIconSize(self, size = 32):
        self.playonlinuxSettings.setSetting("ICON_SIZE",str(size))
        views.InstalledApps.setIconSize(self, size)