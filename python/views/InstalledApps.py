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

class InstalledApps(wx.TreeCtrl, Observer, Observable):
    def __init__(self, frame, controller, style = wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|UIHelper().widgetBorders()):
        wx.TreeCtrl.__init__(self, frame, 105, style=style)
        Observer.__init__(self)
        Observable.__init__(self)
        
        self.frame = frame
        self.controller = controller
        self.SetSpacing(0)
        self.SetIndent(5)
        self.iconSize = 22
        self.searchFilter = ""

    def setSearchFilter(self, text):
        self.searchFilter = text
        
    def writeShortcuts(self, searchFilter = ""):
        self.DeleteAllItems()       
        self.SetImageList(wx.ImageList(1,1))
        
        try:
            self.imagesAppList.Destroy()
        except AttributeError: #imagesAppList does not exist yet, no problem
            pass
            
        self.imagesAppList = wx.ImageList(self.iconSize, self.iconSize)
        self.SetImageList(self.imagesAppList)
        
        root = self.AddRoot("")
        i = 0
        for shortcut in self.controller.getInstalledApps():
           if(searchFilter in shortcut.lower()):
               self.imagesAppList.Add(ShortcutIcon(shortcut, self.iconSize).getBitmap())
               self.AppendItem(root, shortcut, i)
               i+=1
            
    def setIconSize(self, size = 32):
        self.iconSize = size
        self.refresh()
    
    def getIconSize(self):
        return self.iconSize
         
    def refresh(self):
        self.writeShortcuts(self.searchFilter)
        self.update()
        
    def notify(self):
        self.refresh()
   
    def getSelectedShortcut(self):
        selectedName = self.GetItemText(self.GetSelection()) # FIXME ? .encode("utf-8","replace")
        
        if(selectedName == ""):
            raise ErrNoProgramSelected
            
        return selectedName