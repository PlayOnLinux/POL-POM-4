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
encoding = 'utf-8'

# Python imports
import os, getopt, sys, urllib, signal, string, time, webbrowser, gettext, locale, sys, shutil, subprocess, signal, threading
import wx, wx.aui

# PlayOnLinux imports
from lib.Context import Context
from lib.System import System
from lib.Script import PrivateScript
from POLWeb import POLWeb
from lib.UI import UI
from lib.ConfigFile import GlobalConfigFile

import lib.playonlinux as playonlinux
import guiv3 as gui, gui_server#, install, options, wine_versions as wver, sp, configure, debug, gui_server
#import irc as ircgui



class MainWindow(wx.Frame):
    def __init__(self, context, parent, id, title):
        
        # Get context, settings, and UI rules
        self.context = context
        self.ui = UI(self.context);
        
        self.playonlinuxSettings = GlobalConfigFile(self.context)
       
        # Some vars
        self.windowList = {}    # List of POL_SetupWindow opened
        self.registeredPid = [] # List of bash pids belonging to POL 
        self.windowOpened = 0   # Number of POL_SetupWindow opened
        
        
        # Manage updater
        self.updater = POLWeb(context)
        self.updater.start()

        # These lists contain the dock links and images 
        self.menuElem = {}
        self.menuImage = {}

        # Catch CTRL+C
        signal.signal(signal.SIGINT, self.ForceClose)
        
        # Init window
        self.drawWindow(parent, id, title)
        

        # Widgets
        self.images = wx.ImageList(self.iconSize, self.iconSize)
        self.imagesEmpty = wx.ImageList(1,1)


        self.list_game = wx.TreeCtrl(self, 105, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_game.SetSpacing(0);
        self.list_game.SetIndent(5);
        self.list_game.SetImageList(self.images)

        self._mgr = wx.aui.AuiManager(self)
        self.menu_gauche = wx.Panel(self,-1)
        self._mgr.AddPane(self.list_game, wx.CENTER)


        self.filemenu = wx.Menu()
        
        ### On MacOS X, preference is always on the main menu
        if(os.environ["POL_OS"] == "Mac"):
            prefItem = self.filemenu.Append(wx.ID_PREFERENCES, text = "&Preferences")
            self.Bind(wx.EVT_MENU, self.Options, prefItem)

        ### File menu
        self.filemenu.Append(wx.ID_OPEN, _("Run"))
        self.filemenu.Append(wx.ID_ADD, _("Install"))
        self.filemenu.Append(wx.ID_DELETE, _("Remove"))
        self.filemenu.AppendSeparator()
        self.filemenu.Append(216, _("Donate"))
        self.filemenu.Append(wx.ID_EXIT, _("Exit"))

        ### Display menu
        self.displaymenu = wx.Menu()
        self.icon16 = self.displaymenu.AppendRadioItem(501, _("Small icons"))
        self.icon24 = self.displaymenu.AppendRadioItem(502, _("Medium icons"))
        self.icon32 = self.displaymenu.AppendRadioItem(503, _("Large icons"))
        self.icon48 = self.displaymenu.AppendRadioItem(504, _("Very large icons"))
        
        if(self.iconSize == 16):
            self.icon16.Check(True)
        if(self.iconSize == 24):
            self.icon24.Check(True)
        if(self.iconSize == 32):
            self.icon32.Check(True)
        if(self.iconSize == 48):
            self.icon48.Check(True)


        # Expert menu
        self.expertmenu = wx.Menu()
        self.addMenuItem(107,  _('Manage Wine versions'), "wine.png", self.expertmenu)

        if(self.context.getOS == "Mac"):
            self.expertmenu.AppendSeparator()
            self.addMenuItem(113,  _('Read a PC cdrom'), "cdrom.png", self.expertmenu)
            

        self.expertmenu.AppendSeparator()
        self.addMenuItem(108,  _('Run a local script'), "run.png", self.expertmenu)
        self.addMenuItem(115,  _('Close all {0} software').format(self.context.getAppName()), "wineserver.png", self.expertmenu)
        self.addMenuItem(110, _("{0} debugger").format(self.context.getAppName()), "bug.png", self.expertmenu)
        self.addMenuItem(109, _('{0} console').format(self.context.getAppName()), "polshell.png", self.expertmenu)
       
        self.expertmenu.AppendSeparator()
        self.addMenuItem(112, self.context.getAppName()+" online", "playonlinux_online.png", self.expertmenu)
        self.addMenuItem(111, _("{0} messenger").format(self.context.getAppName()), "people.png", self.expertmenu)
        
        # Option menu
        self.optionmenu = wx.Menu()
        
        self.addMenuItem(221, _("Internet"), "internet.png", self.optionmenu)
        self.addMenuItem(212,  _("File associations"), "extensions.png", self.optionmenu)
        self.addMenuItem(213,  _("Plugin manager"), "plugins.png", self.optionmenu)

        self.help_menu = wx.Menu()
        self.addMenuItem(wx.ID_ABOUT,  _('About {0}').format(self.context.getAppName()), None, self.help_menu)

        self.pluginsmenu = wx.Menu()

        plugin_files = os.listdir(self.context.getAppPath()+"/plugins")
        plugin_files.sort()
        self.plugin_list = []
        
        for plugin in plugin_files:
            if(os.path.exists(self.context.getUserRoot()+"/plugins/"+plugin+"/scripts/menu")):
                if(os.path.exists(self.context.getUserRoot()+"/plugins/"+plugin+"/enabled")):

                    plugin_icon = self.context.getUserRoot()+"/plugins/"+plugin+"/icon"
                    
                    if(not os.path.exists(plugin_icon)):
                        plugin_icon = self.context.getAppPath()+"/etc/playonlinux16.png"

                    self.addMenuItem(300+self+j, plugin, plugin_icon, self.pluginsmenu)
                    wx.EVT_MENU(self, 300+self.j, self.run_plugin)
                    self.plugin_list.append(plugin)

        if(len(self.plugin_list) > 0):
            self.pluginsmenu.AppendSeparator()

        self.option_item_p = wx.MenuItem(self.expertmenu, 214, _("Plugin manager"))
        self.option_item_p.SetBitmap(wx.Bitmap(self.context.getAppPath()+"/etc/onglet/package-x-generic.png"))
        self.pluginsmenu.AppendItem(self.option_item_p)

     

        self.last_string = ""

        self.sb = wx.StatusBar(self, -1 )
        self.sb.SetFieldsCount(2)
        self.sb.SetStatusWidths([self.GetSize()[0], -1])
        self.sb.SetStatusText("", 0)

        if(os.environ["POL_OS"] == "Mac"):
            hauteur = 2;
        else:
            hauteur = 6;
        self.jauge_update = wx.Gauge(self.sb, -1, 100, (self.GetSize()[0]-100, hauteur), size=(100,16))
        self.jauge_update.Pulse()
        self.jauge_update.Hide()
        self.SetStatusBar(self.sb)

        #self.helpmenu = wx.MenuItem()
        #self.helpmenu.Append(wx.ID_ABOUT, _("About"))

        self.menubar = wx.MenuBar()
        self.menubar.Append(self.filemenu, _("File"))
        self.menubar.Append(self.displaymenu, _("Display"))
        self.menubar.Append(self.expertmenu, _("Tools"))
        self.menubar.Append(self.optionmenu, _("Settings"))
        self.menubar.Append(self.pluginsmenu, _("Plugins"))
        self.menubar.Append(self.help_menu, "&Help")

        #self.menubar.Append(self.help_menu, _("About"))
        
        self.SetMenuBar(self.menubar)
        iconSize = (32,32)

        self.toolbar = self.CreateToolBar(wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(iconSize)
        self.searchbox = wx.SearchCtrl( self.toolbar, 124, style=wx.RAISED_BORDER )
        self.playTool = self.toolbar.AddLabelTool(wx.ID_OPEN, _("Run"), wx.Bitmap(self.context.getAppPath()+"/resources/images/toolbar/play.png"))
        self.stopTool = self.toolbar.AddLabelTool(123, _("Close"), wx.Bitmap(self.context.getAppPath()+"/resources/images/toolbar/stop.png"))

        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_ADD, _("Install"), wx.Bitmap(self.context.getAppPath()+"/resources/images/toolbar/install.png"))
        self.removeTool = self.toolbar_remove = self.toolbar.AddLabelTool(wx.ID_DELETE, _("Remove"), wx.Bitmap(self.context.getAppPath   ()+"/resources/images/toolbar/delete.png"))
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(121, _("Configure"), wx.Bitmap(self.context.getAppPath()+"/resources/images/toolbar/configure.png"))

        try: 
                self.toolbar.AddStretchableSpace()
                self.SpaceHack = False
        except:
                # wxpython 2.8 does not support AddStretchableSpace(). This is a dirty workaround for this.
                self.dirtyHack = wx.StaticText(self.toolbar)
                self.SpaceHack = True
                self.toolbar.AddControl( self.dirtyHack ) 
                self.UpdateSearchHackSize()

        try:
                self.toolbar.AddControl( self.searchbox , _("Search")) 
        except:
                self.toolbar.AddControl( self.searchbox ) 
                self.searchbox.SetDescriptiveText(_("Search"))


        self.toolbar.Realize()
        self.Reload(self)
        wx.EVT_MENU(self, wx.ID_OPEN,  self.Run)
        wx.EVT_MENU(self, 123,  self.RKill)

        wx.EVT_MENU(self, wx.ID_ADD,  self.InstallMenu)
        wx.EVT_MENU(self, wx.ID_ABOUT,  self.About)
        wx.EVT_MENU(self,  wx.ID_EXIT,  self.ClosePol)
        wx.EVT_MENU(self,  wx.ID_DELETE,  self.UninstallGame)

        # Display
        wx.EVT_MENU(self, 501,  self.iconDisplay)
        wx.EVT_MENU(self, 502,  self.iconDisplay)
        wx.EVT_MENU(self, 503,  self.iconDisplay)
        wx.EVT_MENU(self, 504,  self.iconDisplay)
        wx.EVT_MENU(self, 505,  self.displayMen)

        # Expert
        wx.EVT_MENU(self, 101,  self.Reload)
        wx.EVT_MENU(self, 107,  self.WineVersion)
        wx.EVT_MENU(self, 108,  self.Executer)
        wx.EVT_MENU(self, 109,  self.PolShell)
        wx.EVT_MENU(self, 110,  self.BugReport)
        wx.EVT_MENU(self, 111,  self.OpenIrc)
        wx.EVT_MENU(self, 112,  self.POLOnline)
        wx.EVT_MENU(self, 113,  self.PCCd)
        wx.EVT_MENU(self, 115,  self.killall)
        wx.EVT_MENU(self, 121,  self.Configure)
        wx.EVT_MENU(self, 122,  self.Package)
        wx.EVT_TEXT(self, 124,  self.Reload)

        #Options
        wx.EVT_MENU(self, 210,  self.Options)
        wx.EVT_MENU(self, 211,  self.Options)
        wx.EVT_MENU(self, 212,  self.Options)
        wx.EVT_MENU(self, 213,  self.Options)
        wx.EVT_MENU(self, 214,  self.Options)
        wx.EVT_MENU(self, 215,  self.Options)

        wx.EVT_MENU(self, 216,  self.donate)

        wx.EVT_CLOSE(self, self.ClosePol)
        wx.EVT_TREE_ITEM_ACTIVATED(self, 105, self.Run)
        wx.EVT_TREE_SEL_CHANGED(self, 105, self.Select)


        # PlayOnLinux main timer
        self.timer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.TimerAction, self.timer)
        self.timer.Start(1000)
        self.Timer_LastShortcutList = None
        self.Timer_LastIconList = None
  
        # SetupWindow timer. The server is in another thread and GUI must be run from the main thread
        self.SetupWindowTimer = wx.Timer(self, 2)
        self.Bind(wx.EVT_TIMER, self.SetupWindowAction, self.SetupWindowTimer)
        self.SetupWindowTimer_action = None
        self.SetupWindowTimer.Start(100)
        self.SetupWindowTimer_delay = 100

        #Pop-up menu for game list: beginning
        wx.EVT_TREE_ITEM_MENU(self, 105, self.RMBInGameList)
        wx.EVT_MENU(self, 230, self.RWineConfigurator)
        wx.EVT_MENU(self, 231, self.RRegistryEditor)
        wx.EVT_MENU(self, 232, self.GoToAppDir)
        wx.EVT_MENU(self, 233, self.ChangeIcon)
        wx.EVT_MENU(self, 234, self.UninstallGame)
        wx.EVT_MENU(self, 235, self.RKill)
        wx.EVT_MENU(self, 236, self.ReadMe)
        self.Bind(wx.EVT_SIZE, self.ResizeWindow)

        self.MgrAddPage()

    def drawWindow(self, parent, id, title):
        wx.Frame.__init__(self, parent, 1000, title, size = (515,450))
        self.SetIcon(wx.Icon(self.context.getAppPath()+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        
        ### Window behavior
        # Window size
        self.SetMinSize((400,400))
        self.windowWidth = self.playonlinuxSettings.getIntSetting("MAINWINDOW_WIDTH", default = 450)
        self.windowHeight = self.playonlinuxSettings.getIntSetting("MAINWINDOW_HEIGHT", default = 450)
        self.SetSize((self.windowWidth,self.windowHeight))
        

        # Window position
        self.windowx = self.playonlinuxSettings.getIntSetting("MAINWINDOW_X", default = 30)
        self.windowy = self.playonlinuxSettings.getIntSetting("MAINWINDOW_Y", default = 30)
        self.screen_width = wx.Display().GetGeometry()[2]
        self.screen_height = wx.Display().GetGeometry()[3]

        if(self.screen_width >= self.windowx and self.screen_height >= self.windowy):
            self.SetPosition((self.windowx, self.windowy))
        else:
            self.Center(wx.BOTH)
        
        # Icon size
        self.iconSize = self.playonlinuxSettings.getIntSetting("ICON_SIZE", default = 32)
        
    def ResizeWindow(self, e):
        self.UpdateGaugePos()
        self.UpdateSearchHackSize()
       
    def UpdateSearchHackSize(self):
        if(self.SpaceHack == True):
            self.dirtyHack.SetLabel("")
            self.dirtyHack.SetSize((50,1))

    def UpdateGaugePos(self):
        if(os.environ["POL_OS"] == "Mac"):
            hauteur = 2;
        else:
            hauteur = 6;
        self.jauge_update.SetPosition((self.GetSize()[0]-100, hauteur))

    def SetupWindowTimer_SendToGui(self, recvData):
        recvData = recvData.split("\t")
        while(self.SetupWindowTimer_action != None):
            time.sleep(0.1)
        self.SetupWindowTimer_action = recvData
        
    def SetupWindow_TimerRestart(self, time):
        if(time != self.SetupWindowTimer_delay):
            self.SetupWindowTimer.Stop()
            self.SetupWindowTimer.Start(time)
            self.SetupWindowTimer_delay = time

    def SetupWindowAction(self, event):
        
        if(self.windowOpened == 0):
            self.SetupWindow_TimerRestart(100)
        else:
            self.SetupWindow_TimerRestart(10)

        if(self.SetupWindowTimer_action != None):                           
            return gui_server.readAction(self)
            
           
    def TimerAction(self, event):
        self.StatusRead()
        # We read shortcut folder to see if it has to be rescanned
        currentShortcuts = os.path.getmtime(self.context.getUserRoot()+"/shortcuts")
        currentIcons = os.path.getmtime(self.context.getUserRoot()+"/icones/32")
        if(currentShortcuts != self.Timer_LastShortcutList or currentIcons != self.Timer_LastIconList):
            self.Reload(self)
            self.Timer_LastShortcutList = currentShortcuts
            self.Timer_LastIconList = currentIcons
            
    def MgrAddPage(self):
        try:
            self.LoadSize = int(playonlinux.GetSettings("PANEL_SIZE"))
        except:
            self.LoadSize = 150

        try:
            self.LoadPosition = playonlinux.GetSettings("PANEL_POSITION")
        except:
            self.LoadPosition = "LEFT"

        if(self.LoadSize < 20):
            self.LoadSize = 20
        if(self.LoadSize > 1000):
            self.LoadSize = 1000


        if(self.LoadPosition == "LEFT"):
            self._mgr.AddPane(self.menu_gauche, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Left().BestSize((self.LoadSize,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
        else:
            self._mgr.AddPane(self.menu_gauche, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Right().BestSize((self.LoadSize,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
        self.menu_gauche.Show()

        self._mgr.Update()

    def displayMen(self, event):
        playonlinux.SetSettings("PANEL_POSITION","LEFT")
        if(self.panDisplay.IsChecked()):
            self.MgrAddPage()

    def StatusRead(self):
        self.sb.SetStatusText(self.updater.sendToStatusBarStr, 0)
        if(self.updater.Gauge == True):
            perc = self.updater.perc
            if(perc == -1):
                self.jauge_update.Pulse()
            else:
                try:
                    self.installFrame.percentageText.SetLabel(str(perc)+" %")
                except:
                    pass
                self.jauge_update.SetValue(perc)
            self.jauge_update.Show()
        else:
            self.jauge_update.Hide()

        if(self.updater.updating == True):
            self.sb.Show()
            try:
                self.installFrame.panelItems.Hide()
                self.installFrame.panelManual.Hide()
                self.installFrame.panelWait.Show()
                try:
                    if(self.playing == False):
                        self.installFrame.animation_wait.Play()
                        self.playing = True
                except:
                    self.playing = False
            except:
                pass
        else:
            self.sb.Hide()
            try:
                if(self.installFrame.currentPanel == 1):
                    self.installFrame.panelManual.Show()
                else:
                    self.installFrame.panelItems.Show()
                self.installFrame.panelWait.Hide()
                self.installFrame.animation_wait.Stop()
                self.playing = False
                self.installFrame.Refresh()
            except:
                pass
                
        self.alert = self.updater.getAlert()
        if(self.alert != None):
            wx.MessageBox(self.alert, self.context.getAppName())

    def RMBInGameList(self, event):
        self.GameListPopUpMenu = wx.Menu()

        self.ConfigureWine = wx.MenuItem(self.GameListPopUpMenu, 230, _("Configure Wine"))
        self.ConfigureWine.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/run.png"))
        self.GameListPopUpMenu.AppendItem(self.ConfigureWine)

        self.RegistryEditor = wx.MenuItem(self.GameListPopUpMenu, 231, _("Registry Editor"))
        self.RegistryEditor.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/regedit.png"))
        self.GameListPopUpMenu.AppendItem(self.RegistryEditor)

        self.GotoAppDir = wx.MenuItem(self.GameListPopUpMenu, 232, _("Open the application's directory"))
        self.GotoAppDir.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/folder-wine.png"))
        self.GameListPopUpMenu.AppendItem(self.GotoAppDir)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 236, _("Read the manual"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/manual.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 233, _("Set the icon"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/change_icon.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 234, _("Remove"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/delete.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 235, _("Close this application"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(self.context.getUserRoot()+"/resources/images/menu/media-playback-stop.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.PopupMenu(self.GameListPopUpMenu, event.GetPoint())


    def addMenuItem(self, id, title, icon, menu):
        if(icon != None):
            item = wx.MenuItem(menu, id, _(title))
            os.chdir(self.context.getAppPath()+"/resources/images/menu/")
            
            item.SetBitmap(wx.Bitmap(icon))
            menu.AppendItem(item)
        else:
            menu.Append(id, title)
            
        
    def RWineConfigurator(self, event):
        self.RConfigure(_("Configure Wine"), "nothing")

    def RKill(self, event):
        self.RConfigure(_("KillApp"), "nothing")

    def ReadMe(self, event):
        game_exec = self.GetSelectedProgram()
        if(os.path.exists(os.environ["POL_USER_ROOT"]+"/configurations/manuals/"+game_exec)):
            playonlinux.POL_Open(os.environ["POL_USER_ROOT"]+"/configurations/manuals/"+game_exec)
        else:
            wx.MessageBox(_("No manual found for {0}").format(game_exec), self.context.getAppName())

    def RRegistryEditor(self, event):
        self.RConfigure(_("Registry Editor"), "nothing")

    def run_plugin(self, event):
        game_exec = self.GetSelectedProgram()
        plugin=self.plugin_list[event.GetId()-300]
        try :
            os.system("bash \""+self.context.getUserRoot()+"/plugins/"+plugin+"/scripts/menu\" \""+game_exec+"\"&")
        except :
            pass

    def iconDisplay(self, event):
        iconEvent=event.GetId()

        if(iconEvent == 501):
            self.iconSize = 16
        if(iconEvent == 502):
            self.iconSize = 24
        if(iconEvent == 503):
            self.iconSize = 32
        if(iconEvent == 504):
            self.iconSize = 48

        playonlinux.SetSettings("ICON_SIZE",str(self.iconSize))
        self.list_game.SetImageList(self.imagesEmpty)
        self.images.Destroy()
        self.images = wx.ImageList(self.iconSize, self.iconSize)
        self.list_game.SetImageList(self.images)


        self.Reload(self)

    def OpenIrc(self, event):
        self.irc = ircgui.IrcClient(self)
        self.irc.Center(wx.BOTH)
        self.irc.Show(True)

    def UpdateGIT(self, event):
        os.system("bash \""+self.context.getUserRoot()+"/bash/update_git\"&")


    def GoToAppDir(self, event):
        self.game_exec = self.GetSelectedProgram()
        playonlinux.open_folder(self.game_exec)

    def ChangeIcon(self, event):
        self.IconDir = self.context.getHomeDir()+"/.local/share/icons/"
        self.SupprotedIconExt = "All|*.xpm;*.XPM;*.png;*.PNG;*.ico;*.ICO;*.jpg;*.JPG;*.jpeg;*.JPEG;*.bmp;*.BMP\
        \|XPM (*.xpm)|*.xpm;*.XPM\
        \|PNG (*.png)|*.png;*.PNG\
        \|ICO (*.ico)|*.ico;*.ICO\
        \|JPG (*.jpg)|*.jpg;*.JPG\
        \|BMP (*.bmp)|*.bmp;*.BMP\
        \|JPEG (*.jpeg)|*.jpeg;*JPEG"
        self.IconDialog = wx.FileDialog(self, "Choose a icon file", self.IconDir, "", self.SupprotedIconExt, wx.OPEN | wx.FD_PREVIEW)
        if self.IconDialog.ShowModal() == wx.ID_OK:
            self.IconFilename=self.IconDialog.GetFilename()
            self.IconDirname=self.IconDialog.GetDirectory()
            IconFile=os.path.join(self.IconDirname,self.IconFilename)
            self.RConfigure("IconChange", IconFile)
            self.IconDialog.Destroy()
            #Pop-up menu for game list: ending

    def Select(self, event):
        game_exec = self.GetSelectedProgram()
        self.read = open(self.context.getUserRoot()+"shortcuts/"+game_exec,"r").readlines()
        self.i = 0;
        self.wine_present = False;
        while(self.i < len(self.read)):
            if("wine " in self.read[self.i]):
                self.wine_present = True;
            self.i += 1

        self.generate_menu(game_exec)
        self.playTool.Enable(True)
        self.stopTool.Enable(True)
        self.removeTool.Enable(True)

    def generate_menu(self, shortcut=None):
        for c in self.menuElem:
            self.menuElem[c].Destroy()

        for c in self.menuImage:
            self.menuImage[c].Destroy()
        try:
            self.menuBitmap.Destroy()
        except:
            pass

        self.menuElem = {}
        self.menuImage = {}

        i = 0;
        self.menuGaucheAddTitle("pol_title", self.context.getAppName(), i)
        i+=1
        self.menuGaucheAddLink("pol_prgm_install", _("Install a program"), i,self.context.getAppPath()+"/resources/images/menu/add.png",self.InstallMenu)
        i+=1
        self.menuGaucheAddLink("pol_prgm_settings", _("Settings"), i,self.context.getAppPath()+"/resources/images/menu/settings.png",self.Options)
        i+=1
        self.menuGaucheAddLink("pol_prgm_messenger", _("Messenger"), i,self.context.getAppPath()+"/resources/images/menu/people.png",self.OpenIrc)
        if(os.path.exists(os.environ["PLAYONLINUX"]+"/.git/")):
            i+=1
            self.menuGaucheAddLink("pol_git", _("Update GIT"), i,self.context.getAppPath()+"/resources/images/menu/update_git.png",self.UpdateGIT)

        if(shortcut != None):
            i+=2
            self.menuGaucheAddTitle("prgm_title", shortcut, i)
            i+=1
            self.menuGaucheAddLink("pol_prgm_run", _("Run"), i,self.context.getAppPath()+"/resources/images/menu/media-playback-start.png",self.Run)
            i+=1
            self.menuGaucheAddLink("pol_prgm_kill", _("Close"), i,self.context.getAppPath()+"/resources/images/menu/media-playback-stop.png",self.RKill)
            i+=1
            self.menuGaucheAddLink("pol_prgm_rundebug", _("Debug"), i,self.context.getAppPath()+"/resources/images/menu/bug.png",self.RunDebug)
            i+=1
            self.menuGaucheAddLink("pol_prgm_configure", _("Configure"), i,self.context.getAppPath()+"/resources/images/menu/run.png",self.Configure)
            i+=1
            self.menuGaucheAddLink("pol_prgm_shortcut", _("Create a shortcut"), i,self.context.getAppPath()+"/resources/images/menu/shortcut.png",self.Package)
            i+=1
            self.menuGaucheAddLink("pol_prgm_adddir", _("Open the directory"), i,self.context.getAppPath()+"/resources/images/menu/folder-wine.png",self.GoToAppDir)

            if(os.path.exists(os.environ["POL_USER_ROOT"]+"/configurations/manuals/"+shortcut)):
                i+=1
                self.menuGaucheAddLink("pol_prgm_readme", _("Read the manual"), i,self.context.getAppPath()+"/resources/images/menu/manual.png",self.ReadMe)

            i+=1
            self.menuGaucheAddLink("pol_prgm_uninstall", _("Uninstall"), i,self.context.getAppPath()+"/resources/images/menu/window-close.png",self.UninstallGame)


            self.linksfile = os.environ["POL_USER_ROOT"]+"/configurations/links/"+shortcut
            if(os.path.exists(self.linksfile)):
                self.linksc = open(self.linksfile,"r").read().split("\n")
                for line in self.linksc:
                    if("|" in line):
                        line = line.split("|")
                        i+=1
                        if("PROFILEBUTTON/" in line[0]):
                            line[0] = line[0].replace("PROFILEBUTTON/","")

                        self.menuGaucheAddLink("url_"+str(i), line[0], i,self.context.getUserRoot()+"/resources/images/menu/star.png",None,line[1])

            icon = os.environ["POL_USER_ROOT"]+"/icones/full_size/"+shortcut

            self.perspective = self._mgr.SavePerspective().split("|")
            self.perspective = self.perspective[len(self.perspective) - 2].split("=")

            left_pos = (int(self.perspective[1]) - 50)/2
            if(left_pos <= 0):
                left_pos = (200-48)/2

            if(os.path.exists(icon)):
                try:
                    self.bitmap = wx.Image(icon)
                    if(self.bitmap.GetWidth() >= 48):
                        self.bitmap.Rescale(48,48,wx.IMAGE_QUALITY_HIGH)
                        self.bitmap = self.bitmap.ConvertToBitmap()
                        self.menuBitmap = wx.StaticBitmap(self.menu_gauche, id=-1, bitmap=self.bitmap, pos=(left_pos,20+(i+2)*20))
                except:
                    pass

    def menuGaucheAddTitle(self,id,text,pos):
        self.menuElem[id] = wx.StaticText(self.menu_gauche, -1, text,pos=(5,5+pos*20))
        self.menuElem[id].SetForegroundColour((0,0,0)) # For dark themes
        self.menuElem[id].SetFont(self.ui.getFontTitle())


    def menuGaucheAddLink(self,id,text,pos,image,evt,url=None):
        if(os.path.exists(image)):
            menu_icone = image
        else:
            menu_icone = self.context.getAppPath()+"/etc/playonlinux.png"

        try:
            self.bitmap = wx.Image(menu_icone)
            self.bitmap.Rescale(16,16,wx.IMAGE_QUALITY_HIGH)
            self.bitmap = self.bitmap.ConvertToBitmap()
            self.menuImage[id] = wx.StaticBitmap(self.menu_gauche, id=-1, bitmap=self.bitmap, pos=(10,15+pos*20))

        except:
            pass

        if(url == None):
            self.menuElem[id] = wx.HyperlinkCtrl(self.menu_gauche, 10000+pos, text, "", pos=(35,15+pos*20))
        else:
            self.menuElem[id] = wx.HyperlinkCtrl(self.menu_gauche, 10000+pos, text, url, pos=(35,15+pos*20))

        self.menuElem[id].SetNormalColour(wx.Colour(0,0,0))
        self.menuElem[id].SetVisitedColour(wx.Colour(0,0,0))
        self.menuElem[id].SetHoverColour(wx.Colour(100,100,100))

        if(evt != None):
            wx.EVT_HYPERLINK(self, 10000+pos, evt)

    def donate(self, event):
        if(os.environ["POL_OS"] == "Mac"):
            webbrowser.open("http://www.playonmac.com/en/donate.html")
        else:
            webbrowser.open("http://www.playonlinux.com/en/donate.html")

    def Reload(self, event):
        self.games = os.listdir(self.context.getUserRoot()+"shortcuts/")
        self.games.sort()
        
        try:
            self.games.remove(".DS_Store")
        except:
            pass
            
        self.list_game.DeleteAllItems()
        self.images.RemoveAll()
        root = self.list_game.AddRoot("")
        self.i = 0
        if(self.iconSize <= 32):
            self.iconFolder = "32";
        else:
            self.iconFolder = "full_size";
        for game in self.games: #METTRE EN 32x32
            if(self.searchbox.GetValue().encode("utf-8","replace").lower() in game.lower()):
                if(not os.path.isdir(self.context.getUserRoot()+"/shortcuts/"+game)):
                    if(os.path.exists(self.context.getUserRoot()+"/icones/"+self.iconFolder+"/"+game)):
                         file_icone = self.context.getUserRoot()+"/icones/"+self.iconFolder+"/"+game
                    else:
                        file_icone = self.context.getAppPath()+"/etc/playonlinux.png"

                    try:
                        self.bitmap = wx.Image(file_icone)
                        self.bitmap.Rescale(self.iconSize,self.iconSize,wx.IMAGE_QUALITY_HIGH)
                        self.bitmap = self.bitmap.ConvertToBitmap()
                        self.images.Add(self.bitmap)
                    except:
                        pass
                    
                    item = self.list_game.AppendItem(root, game, self.i)
                    self.i += 1
        self.generate_menu(None)

        if(os.environ["POL_OS"] == "Mac"):
            self.playTool.Enable(False)
            self.stopTool.Enable(False)
            self.removeTool.Enable(False)


    def RConfigure(self, function_to_run, firstargument):
        """Starts polconfigurator remotely."""
        game_exec = self.GetSelectedProgram()
        if(game_exec != ""):
            os.system("bash \""+self.context.getAppPath()+"/bash/polconfigurator\" \""+game_exec+"\" \""+function_to_run+"\" \""+firstargument+"\"&")
        else:
            wx.MessageBox(_("Please select a program."), self.context.getAppName())


    def Options(self, event):
        onglet=event.GetId()
        try:
            self.optionFrame.SetFocus()
        except:
            self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(self.context.getAppName()), 2)
            if(onglet == 211):
                self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(self.context.getAppName()), 0)
            if(onglet == 214):
                self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(self.context.getAppName()), 1)
            self.optionFrame.Center(wx.BOTH)
            self.optionFrame.Show(True)

    def killall(self, event):
        os.system("bash \""+self.context.getAppPath()+"/bash/killall\"&")

    def Executer(self, event):
        os.system("bash \""+self.context.getAppPath()+"/bash/expert/Executer\"&")

    def BugReport(self, event):
        try:
            self.debugFrame.Show()
            self.debugFrame.SetFocus()
        except:
            self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(self.context.getAppName()))
            self.debugFrame.Center(wx.BOTH)
            self.debugFrame.Show()


    def POLOnline(self, event):
        os.system("bash \""+self.context.getAppPath()+"/bash/playonlinux_online\" &")

    def PCCd(self, event):
        os.system("bash \""+self.context.getAppPath()+"/bash/read_pc_cd\" &")

    def PolShell(self, event):
        #Variables.run_x_server()
        os.system("bash \""+self.context.getAppPath()+"/bash/expert/PolShell\"&")

    def Configure(self, event):
        game_exec = self.GetSelectedProgram()
        try:
            self.configureFrame.Show(True)
            self.configureFrame.SetFocus()
            if(game_exec != ""):
                self.configureFrame.change_program(game_exec,False)

        except:
            if(game_exec == ""):
                self.configureFrame = configure.MainWindow(self, -1, _("{0} configuration").format(self.context.getAppName()),"default",True)
            else:
                self.configureFrame = configure.MainWindow(self, -1, _("{0} configuration").format(self.context.getAppName()),game_exec.decode("utf-8","replace"),False)


            self.configureFrame.Center(wx.BOTH)
            self.configureFrame.Show(True)

        #os.system("bash \""+self.context.getUserRoot()+"/bash/polconfigurator\" \""+game_exec+"\"&")

    def Package(self, event):
        game_exec = self.GetSelectedProgram()
        os.system("bash \""+self.context.getAppPath()+"/bash/make_shortcut\" \""+game_exec.encode("utf-8","replace")+"\"&")

    def UninstallGame(self, event):
        game_exec = self.GetSelectedProgram()
        if(game_exec != ""):
            os.system("bash \""+self.context.getAppPath()+"/bash/uninstall\" \""+game_exec.encode("utf-8","replace")+"\"&")
        else:
            wx.MessageBox(_("Please select a program."), self.context.getAppName())

    def InstallMenu(self, event):
        try:
            self.installFrame.Show(True)
            self.installFrame.SetFocus()
        except:
            self.installFrame = install.InstallWindow(self, -1, _('{0} install menu').format(self.context.getAppName()))
            self.installFrame.Center(wx.BOTH)
            self.installFrame.Show(True)

    def WineVersion(self, event):
        try:
            self.wversion.Show()
            self.wversion.SetFocus()
        except:
            self.wversion = wver.MainWindow(None, -1, _('{0} wine versions manager').format(self.context.getAppName()))
            self.wversion.Center(wx.BOTH)
            self.wversion.Show(True)

    def GetSelectedProgram(self):
        return self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
        
    def Run(self, event, s_debug=False):

        game_exec = self.GetSelectedProgram()
        game_prefix = playonlinux.getPrefix(game_exec)

        if(s_debug == False):
            playonlinux.SetDebugState(game_exec, False)

        if(os.path.exists(os.environ["POL_USER_ROOT"]+"/wineprefix/"+game_prefix)):
            if(game_exec != ""):
                if(playonlinux.GetDebugState(game_exec)):
                    try:
                        self.debugFrame.analyseReal(0, game_prefix)
                        self.debugFrame.Show()
                        self.debugFrame.SetFocus()
                    except:
                        self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(self.context.getAppName()),game_prefix,0)
                        self.debugFrame.Center(wx.BOTH)
                        self.debugFrame.Show()

                os.system("bash "+self.context.getAppPath()+"/bash/run_app \""+game_exec+"\"&")
            else:
                wx.MessageBox(_("Please select a program."), self.context.getAppName())
        else:
            wx.MessageBox(_("The virtual drive associated with {0} ({1}) does no longer exists.").format(game_exec, game_prefix), self.context.getAppName())

    def RunDebug(self, event):
        game_exec = self.GetSelectedProgram()
        game_prefix = playonlinux.getPrefix(game_exec)
        playonlinux.SetDebugState(game_exec, True)
        self.Run(self, True)
 
    def POLDie(self):
        for pid in self.registeredPid:
            os.system("kill -9 -"+pid+" 2> /dev/null")
            os.system("kill -9 "+pid+" 2> /dev/null") 
        app.POLServer.closeServer()
        os._exit(0)

    def POLRestart(self):
        for pid in self.registeredPid:
            os.system("kill -9 -"+pid+" 2> /dev/null")
            os.system("kill -9 "+pid+" 2> /dev/null") 
        app.POLServer.closeServer()
        os._exit(63) # Restart code

    def ForceClose(self, signal, frame): # Catch SIGINT
        print "\nCtrl+C pressed. Killing all processes..."
        self.POLDie()

    def ClosePol(self, event):
        if(playonlinux.GetSettings("DONT_ASK_BEFORE_CLOSING") == "TRUE" or wx.YES == wx.MessageBox(_('Are you sure you want to close all {0} Windows?').format(self.context.getAppName()).decode("utf-8","replace"),self.context.getAppName(), style=wx.YES_NO | wx.ICON_QUESTION)):
            self.SizeToSave = self.GetSize();
            self.PositionToSave = self.GetPosition();
            # Save size and position
            playonlinux.SetSettings("MAINWINDOW_WIDTH",str(self.SizeToSave[0]))
            playonlinux.SetSettings("MAINWINDOW_HEIGHT",str(self.SizeToSave[1] - self.ui.AddMacOffset(56)))
            playonlinux.SetSettings("MAINWINDOW_X",str(self.PositionToSave[0]))
            playonlinux.SetSettings("MAINWINDOW_Y",str(self.PositionToSave[1]))
            self._mgr.UnInit()
            # I know, that's very ugly, but I have no choice for the moment
            
            self.perspective = self._mgr.SavePerspective().split("|")
            self.perspective = self.perspective[len(self.perspective) - 2].split("=")

            self.DockType = self.perspective[0]
            self.mySize = 200
            self.myPosition = "LEFT"

            if(self.DockType == "dock_size(4,0,0)"):
                self.mySize = int(self.perspective[1]) - 2
                self.myPosition = "LEFT"

            if(self.DockType == "dock_size(2,0,1)" or self.DockType == "dock_size(2,0,0)" or "dock_size(2," in self.DockType):
                self.mySize = int(self.perspective[1]) - 2
                self.myPosition = "RIGHT"

            playonlinux.SetSettings("PANEL_SIZE",str(self.mySize))
            playonlinux.SetSettings("PANEL_POSITION",str(self.myPosition))

            self.POLDie()
        return None

    def About(self, event):
        self.aboutBox = wx.AboutDialogInfo()
        if(os.environ["POL_OS"] == "Linux"):
            self.aboutBox.SetIcon(wx.Icon(self.context.getAppPath()+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))


        self.aboutBox.SetName(self.context.getAppName())
        self.aboutBox.SetVersion(self.context.getAppVersion())
        self.aboutBox.SetDescription(_("Run your Windows programs on "+os.environ["POL_OS"]+" !"))
        self.aboutBox.SetCopyright("© 2007-2012 "+_("PlayOnLinux and PlayOnMac team\nUnder GPL licence version 3"))
        self.aboutBox.AddDeveloper(_("Developer and Website: ")+"Tinou (Pâris Quentin), MulX (Petit Aymeric)")
        self.aboutBox.AddDeveloper(_("Scriptors: ")+"GNU_Raziel")
        self.aboutBox.AddDeveloper(_("Packager: ")+"MulX (Petit Aymeric), Tinou (Pâris Quentin)")
        self.aboutBox.AddDeveloper(_("Icons:")+"Faenza-Icons http://tiheum.deviantart.com/art/Faenza-Icons-173323228")
        self.aboutBox.AddDeveloper(_("The following people contributed to this program: ")+"kiplantt, Salvatos, Minchul")
        self.aboutBox.AddTranslator(_("Translations:"))
        self.aboutBox.AddTranslator(_("Read TRANSLATORS file"))

        if(os.environ["POL_OS"] == "Mac"):
            self.aboutBox.SetWebSite("http://www.playonmac.com")
        else:
            self.aboutBox.SetWebSite("http://www.playonlinux.com")
        wx.AboutBox(self.aboutBox)



class PlayOnLinuxApp(wx.App):
    def OnInit(self):
        self.context = Context()
        close = False
        exe_present = False
        self.context.initLanguage()
        
        os.system("bash "+self.context.getAppPath()+"/bash/startup")
        self.systemCheck()
        
        
        for f in  sys.argv[1:]:
            self.MacOpenFile(f)
            if(".exe" in f or ".EXE" in f):
                exe_present = True
            close = True

        if(close == True and exe_present == False):
            os._exit(0)

        self.SetClassName(self.context.getAppName())
        self.SetAppName(self.context.getAppName())

        
        self.frame = MainWindow(self.context, None, -1, self.context.getAppName())
        
        # Gui Server
        self.POLServer = gui_server.gui_server(self.context, self.frame)
        self.POLServer.start()
        self.POLServer.waitForServer()
        
        os.system("bash \"$PLAYONLINUX/bash/startup_after_server\" &")
   
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        
        return True

    def _executableFound(self, executable):
        devnull = open('/dev/null', 'wb')
        try:
            returncode = subprocess.call(["which",executable],stdout=devnull)
            return (returncode == 0)
        except:
            return False

    def _singleCheck(self, executable, package, fatal):
        if not self._executableFound(executable):
            message = _("{0} cannot find {1}")
            if package is not None:
                message += _(" (from {2})")

            if fatal:
                verdict = _("You need to install it to continue")
            else:
                verdict = _("You should install it to use {0}")

            wx.MessageBox(("%s\n\n%s" % (message, verdict)).format(self.context.getAppName(), executable, package), _("Error"))

            if fatal:
                os._exit(0)

    def singleCheck(self, executable, package=None):
        self._singleCheck(executable, package, False)

    def singleCheckFatal(self, executable, package=None):
        self._singleCheck(executable, package, True)

    def systemCheck(self):
        #### Root uid check
        if(System.isRunAsRoot()):
            wx.MessageBox(_("{0} is not supposed to be run as root. Sorry").format(self.context.getAppName()),_("Error"))
            os._exit(0)

        #### 32 bits OpenGL check
        check_gl = PrivateScript(self.context, "check_gl",["x86"])
        returncode = check_gl.run()
        
        if(os.environ["POL_OS"] == "Linux" and returncode != 0):
            wx.MessageBox(_("{0} is unable to find 32bits OpenGL libraries.\n\nYou might encounter problem with your games").format(self.context.getAppName()),_("Error"))
            os.environ["OpenGL32"] = "0"
        else:
            os.environ["OpenGL32"] = "1"

        #### 64 bits OpenGL check
        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            try:
                returncode=subprocess.call([os.environ["PLAYONLINUX"]+"/bash/check_gl","amd64"])
            except:
                returncode=255
        if(os.environ["AMD64_COMPATIBLE"] == "True" and os.environ["POL_OS"] == "Linux" and returncode != 0):
            wx.MessageBox(_("{0} is unable to find 64bits OpenGL libraries.\n\nYou might encounter problem with your games").format(self.context.getAppName()),_("Error"))
            os.environ["OpenGL64"] = "0"
        else:
            os.environ["OpenGL64"] = "1"

        #### Filesystem check
        if(os.environ["POL_OS"] == "Linux"):
            try:
                returncode=subprocess.call([os.environ["PLAYONLINUX"]+"/bash/check_fs"])
            except:
                returncode=255
            if(os.environ["POL_OS"] == "Linux" and returncode != 0):
                wx.MessageBox(_("Your filesystem might prevent {0} from running correctly.\n\nPlease open {0} in a terminal to get more details").format(self.context.getAppName()),_("Error"))

        if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
            if(playonlinux.GetSettings("SEND_REPORT") == ""):
                if(wx.YES == wx.MessageBox(_('Do you want to help {0} to make a compatibility database?\n\nIf you click yes, the following things will be sent to us anonymously the first time you run a Windows program:\n\n- You graphic card model\n- Your OS version\n- If graphic drivers are installed or not.\n\n\nThese information will be very precious for us to help people.').format(self.context.getAppName()).decode("utf-8","replace"), self.context.getAppName(),style=wx.YES_NO | wx.ICON_QUESTION)):
                    playonlinux.SetSettings("SEND_REPORT","TRUE")
                else:
                    playonlinux.SetSettings("SEND_REPORT","FALSE")

        #### Other import checks
        self.singleCheckFatal("nc", package="Netcat")
        self.singleCheckFatal("tar")
        self.singleCheckFatal("cabextract")
        self.singleCheckFatal("convert", package="ImageMagick")
        self.singleCheckFatal("wget", package="Wget")
        self.singleCheckFatal("gpg", package="GnuPG")

        if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
            self.singleCheck("xterm")
        self.singleCheck("gettext.sh", package="gettext")  # gettext-base on Debian
        self.singleCheck("icotool", package="icoutils")
        self.singleCheck("wrestool", package="icoutils")
        self.singleCheck("wine", package="Wine")
        self.singleCheck("unzip", package="InfoZIP")
        self.singleCheck("7z", package="P7ZIP full")  # p7zip-full on Debian

    def BringWindowToFront(self):
        try: # it's possible for this event to come when the frame is closed
            self.GetTopWindow().Raise()
        except:
            pass

    def MacOpenFile(self, filename):
        file_extension = string.split(filename,".")
        file_extension = file_extension[len(file_extension) - 1]
        if(file_extension == "desktop"): # Un raccourcis Linux
            content = open(filename,"r").readlines()
            i = 0
            while(i < len(content)):
                #wx.MessageBox(content[i], "PlayOnLinux", wx.OK)

                if("Path=" in content[i]):
                    cd_app = content[i].replace("Path=","").replace("\n","")
                if("Exec=" in content[i]):
                    exec_app = content[i].replace("Exec=","").replace("\n","")
                i += 1
            if(":\\\\\\\\" in exec_app):
                exec_app = exec_app.replace("\\\\","\\")
            try:
                os.system("cd \""+cd_app+"\" && "+exec_app+" &")
            except:
                pass

        elif(file_extension == "exe" or file_extension == "EXE"):
            os.system("bash \"$PLAYONLINUX/bash/run_exe\" \""+filename+"\" &")

        elif(file_extension == "pol" or file_extension == "POL"):
            if(wx.YES == wx.MessageBox(_('Are you sure you want to install {0} package?').format(filename).decode("utf-8","replace"), self.context.getAppName(),style=wx.YES_NO | wx.ICON_QUESTION)):
                os.system("bash \"$PLAYONLINUX/bash/playonlinux-pkg\" -i \""+filename+"\" &")
        else:
            playonlinux.open_document(filename,file_extension.lower())

    def MacOpenURL(self, url):
        if(os.environ["POL_OS"] == "Mac" and "playonlinux://" in url):
            wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnLinux"), self.context.getAppName())
        if(os.environ["POL_OS"] == "Linux" and "playonmac://" in url):
            wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnMac"), self.context.getAppName())

        os.system("bash \"$PLAYONLINUX/bash/playonlinux-url_handler\" \""+url+"\" &")

    def MacReopenApp(self):
        #sys.exit()
        self.BringWindowToFront()


app = PlayOnLinuxApp(redirect=False)
app.MainLoop()