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
import wx, wx.aui

from views.UIHelper import UIHelper

class Menu(wx.Menu):  
    def __init__(self):
        wx.Menu.__init__(self)
        self.uiHelper = UIHelper()
        
    def addItem(self, id, title, icon = None):
        if(icon != None):
            item = wx.MenuItem(self, id, title)            
            item.SetBitmap(self.uiHelper.getBitmap(icon))
            self.AppendItem(item)
        else:
            self.Append(id, title)