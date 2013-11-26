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

class ShortcutIcon(wx.Image):
    def __init__(self, name, iconSize = 32):
        self.env = Environment()
        self._iconSize = iconSize
        
        if(iconSize == 32):
            iconFolder = "32"
        else:
            iconFolder = "full_size"
            
        iconPath = self.env.getUserRoot()+"/icones/"+iconFolder+"/"+name
        if(not os.path.exists(iconPath)):
            iconPath = self.env.getAppPath()+"/etc/playonlinux.png"
         
        try:
           wx.Image.__init__(self, iconPath) 
           self.Rescale(iconSize,iconSize,wx.IMAGE_QUALITY_HIGH)
        except wx._core.PyAssertionError:
           wx.Image.__init__(self, self.env.getAppPath()+"/etc/playonlinux.png")
           self.Rescale(iconSize,iconSize,wx.IMAGE_QUALITY_HIGH)
           
    def getBitmap(self):
        return self.ConvertToBitmap()