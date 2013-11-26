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

from patterns.Observer import Observer
from patterns.Observable import Observable

from services.Environment import Environment
from services.ConfigService import ConfigService

from views.MainWindow.Menu import Menu

class MenuBar(wx.MenuBar, Observer):
    def __init__(self, controller, frame):
        Observer.__init__(self)
        wx.MenuBar.__init__(self)
        self.controller = controller
        self.frame = frame
        self.env = Environment()
        self.configService = ConfigService()
        
        ### File menu
        filemenu = Menu()
        
        # On MacOS X, preference is always on the main menu
        if(self.env.getOS() == "Mac"):
            filemenu.Append(wx.ID_PREFERENCES, text = "&Preferences")
            
        filemenu.addItem(wx.ID_OPEN, _("Run"))
        filemenu.addItem(wx.ID_ADD, _("Install"))
        filemenu.addItem(wx.ID_DELETE, _("Remove"))
        filemenu.AppendSeparator()
        filemenu.addItem(216, _("Donate"))
        filemenu.addItem(wx.ID_EXIT, _("Exit"))

        ### Display menu
        displaymenu = Menu()
        icon16 = displaymenu.AppendRadioItem(501, _("Small icons"))
        icon24 = displaymenu.AppendRadioItem(502, _("Medium icons"))
        icon32 = displaymenu.AppendRadioItem(503, _("Large icons"))
        icon48 = displaymenu.AppendRadioItem(504, _("Very large icons"))
        
        iconSize = self.frame.getAppList().getIconSize()
        
        if(iconSize == 16):
            icon16.Check(True)
        if(iconSize == 24):
            icon24.Check(True)
        if(iconSize == 32):
            icon32.Check(True)
        if(iconSize == 48):
            icon48.Check(True)


        # Expert menu
        expertmenu = Menu()
        expertmenu.addItem(107,  _('Manage Wine versions'), "menu/wine.png")
        
        if(self.env.getOS == "Mac"):
            expertmenu.AppendSeparator()
            expertmenu.addItem(113,  _('Read a PC cdrom'), "menu/cdrom.png")

        expertmenu.AppendSeparator()
        expertmenu.addItem(108,  _('Run a local script'), "menu/run.png")
        expertmenu.addItem(115,  _('Close all {0} software').format(self.configService.getAppName()), "menu/wineserver.png")
        expertmenu.addItem(110, _("{0} debugger").format(self.configService.getAppName()), "menu/bug.png")
        expertmenu.addItem(109, _('{0} console').format(self.configService.getAppName()), "menu/polshell.png")
       
        expertmenu.AppendSeparator()
        expertmenu.addItem(112, self.configService.getAppName()+" online", "menu/playonlinux_online.png")
        expertmenu.addItem(111, _("{0} messenger").format(self.configService.getAppName()), "menu/people.png")
        
        # Option menu
        optionmenu = Menu()
        optionmenu.addItem(221, _("Internet"), "menu/internet.png")
        optionmenu.addItem(212,  _("File associations"), "menu/extensions.png")
        optionmenu.addItem(213,  _("Plugin manager"), "menu/plugins.png")

        
        self.Append(filemenu, _("File"))
        self.Append(displaymenu, _("Display"))
        self.Append(expertmenu, _("Tools"))
        self.Append(optionmenu, _("Settings"))
        
        if(self.env.getOS() != "Mac"):
            help_menu = Menu()
            help_menu.addItem(wx.ID_ABOUT,  _('About {0}').format(self.configService.getAppName()))
            self.Append(help_menu, "&Help")
        else:
            filemenu.addItem(wx.ID_ABOUT,  _('About {0}').format(self.configService.getAppName()))
            
    def refreshPluginMenu(self):
        try: 
            self.pluginsmenu
        except AttributeError:
            pass 
        else:
            self.Remove(5)
            self.pluginsmenu.Destroy()
       
        self.pluginsmenu = Menu()
        
        i = 0
        for plugin in self.controller.getEnabledPlugins():
            self.pluginsmenu.addItem(300 + i, plugin[0], plugin[1])
            i += 1 
            #wx.EVT_MENU(self, 300+self.j, self.run_plugin)

        if(i > 0):
            self.pluginsmenu.AppendSeparator()

        self.pluginsmenu.addItem(214,  _("Plugin manager"), "menu/plugins.png")
        self.Append(self.pluginsmenu, _("Plugins"))
        
        
    def notify(self):
        self.refreshPluginMenu()