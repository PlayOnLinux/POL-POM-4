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

import wx

from services.Environment import Environment
from services.ConfigService import ConfigService


class PolAbout(wx.AboutDialogInfo):
    def __init__(self):
        wx.AboutDialogInfo.__init__(self)
        env = Environment()
        config = ConfigService()
        
        self.SetIcon(wx.Icon(env.getAppPath()+"/resources/icons/playonlinux.png", wx.BITMAP_TYPE_ANY))

        
        self.SetName(config.getAppName())
        self.SetVersion(config.getAppVersion())
        self.SetDescription(_("Run your Windows programs on "+env.getOS()+" !"))
        self.SetCopyright("© 2007-2013 "+_("PlayOnLinux and PlayOnMac team\nUnder GPL licence version 3"))
        self.AddDeveloper(_("Developer and Website: ")+"Tinou (Pâris Quentin), MulX (Petit Aymeric)")
        self.AddDeveloper(_("Scriptors: ")+"GNU_Raziel")
        self.AddDeveloper(_("Packager: ")+"MulX (Petit Aymeric), Tinou (Pâris Quentin)")
        self.AddDeveloper(_("Icons:")+"Faenza-Icons http://tiheum.deviantart.com/art/Faenza-Icons-173323228")
        self.AddDeveloper(_("The following people contributed to this program: ")+"kiplantt, Salvatos, Minchul")
        self.AddTranslator(_("Translations:"))
        self.AddTranslator(_("Read TRANSLATORS file"))

        if(env.getOS() == "Mac"):
            self.SetWebSite("http://www.playonmac.com")
        else:
            self.SetWebSite("http://www.playonlinux.com")
            
    def show(self):
        wx.AboutBox(self) 