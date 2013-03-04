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

# PlayOnLinux

from POLWeb import POLWeb
from lib.UIHelper import UIHelper
from lib.ConfigFile import UserConfigFile
from lib.Context import Context
from lib.System import System
from lib.Shortcut import Shortcut
from lib.Script import PrivateGUIScript
from lib.GuiServer import GuiServer

# Views
from views.SetupWindow import SetupWindow
from views.Question import Question
from views.Message import Message

#, install, options, wine_versions as wver, sp, configure, debug, gui_server
#import irc as ircgui

# Exceptions
class ErrNoProgramSelected(Exception):
   def __str__(self):
      return repr(_("You must select a program"))



class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        
        
        # Get context, settings, and UI rules
        #self.ui = UI(Context());
        self.playonlinuxSettings = UserConfigFile()
        self.playonlinuxSystem = System()
        
        self.windowList = {}    # List of POL_SetupWindow opened
        
        # Manage updater
        self.updater = POLWeb()
        self.updater.start()

        # These lists contain the dock links and images 
        self.menuElem = {}
        self.menuImage = {}
        
        # Init window
        self.drawWindow(parent, id, title)
            
        # Icon size
        self.iconSize = self.playonlinuxSettings.getIntSetting("ICON_SIZE", default = 32)
        
        # Widgets
        self.images = wx.ImageList(self.iconSize, self.iconSize)
        self.imagesEmpty = wx.ImageList(1,1)


        self.appList = wx.TreeCtrl(self, 105, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        self.appList.SetSpacing(0);
        self.appList.SetIndent(5);
        self.appList.SetImageList(self.images)



        # Left panel
        self._mgr = wx.aui.AuiManager(self)
        self.leftPanel = wx.Panel(self,-1)
        self._mgr.AddPane(self.appList, wx.CENTER)
        self.MgrAddPage()
        
        
        # Menubar
        self.drawMenuBar()
        

     

        self.last_string = ""

        self.sb = wx.StatusBar(self, -1 )
        self.sb.SetFieldsCount(2)
        self.sb.SetStatusWidths([self.GetSize()[0], -1])
        self.sb.SetStatusText("", 0)

        self.jauge_update = wx.Gauge(self.sb, -1, 100, (self.GetSize()[0]-100, UIHelper().updateJaugeMarginTop()), size=(100,16))
        self.jauge_update.Pulse()
        self.jauge_update.Hide()
        self.SetStatusBar(self.sb)

        
        self.drawToolBar()
        
        self.Reload(self)


    
        # Program list event
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
        self.Bind(wx.EVT_TIMER, self.readGuiServerQueue, self.SetupWindowTimer)
        self.SetupWindowTimer_action = None
        self.SetupWindowTimer.Start(100)
        self.SetupWindowTimer_delay = 100

        #Pop-up menu for game list: beginning
        wx.EVT_TREE_ITEM_MENU(self, 105, self.RMBInGameList)

        self.Bind(wx.EVT_SIZE, self.ResizeWindow)



    def drawWindow(self, parent, id, title):
        wx.Frame.__init__(self, parent, 1000, title, size = (515,450))
        self.SetIcon(wx.Icon(Context().getAppPath()+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        
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
        

        
        
    def drawMenuBar(self):
        self.filemenu = wx.Menu()
        
        ### On MacOS X, preference is always on the main menu
        if(Context().getOS() == "Mac"):
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

        if(Context().getOS == "Mac"):
            self.expertmenu.AppendSeparator()
            self.addMenuItem(113,  _('Read a PC cdrom'), "cdrom.png", self.expertmenu)
            

        self.expertmenu.AppendSeparator()
        self.addMenuItem(108,  _('Run a local script'), "run.png", self.expertmenu)
        self.addMenuItem(115,  _('Close all {0} software').format(Context().getAppName()), "wineserver.png", self.expertmenu)
        self.addMenuItem(110, _("{0} debugger").format(Context().getAppName()), "bug.png", self.expertmenu)
        self.addMenuItem(109, _('{0} console').format(Context().getAppName()), "polshell.png", self.expertmenu)
       
        self.expertmenu.AppendSeparator()
        self.addMenuItem(112, Context().getAppName()+" online", "playonlinux_online.png", self.expertmenu)
        self.addMenuItem(111, _("{0} messenger").format(Context().getAppName()), "people.png", self.expertmenu)
        
        # Option menu
        self.optionmenu = wx.Menu()
        
        self.addMenuItem(221, _("Internet"), "internet.png", self.optionmenu)
        self.addMenuItem(212,  _("File associations"), "extensions.png", self.optionmenu)
        self.addMenuItem(213,  _("Plugin manager"), "plugins.png", self.optionmenu)

        self.help_menu = wx.Menu()
        self.addMenuItem(wx.ID_ABOUT,  _('About {0}').format(Context().getAppName()), None, self.help_menu)

        self.pluginsmenu = wx.Menu()

        plugin_files = os.listdir(Context().getAppPath()+"/plugins")
        plugin_files.sort()
        self.plugin_list = []
        
        for plugin in plugin_files:
            if(os.path.exists(Context().getUserRoot()+"/plugins/"+plugin+"/scripts/menu")):
                if(os.path.exists(Context().getUserRoot()+"/plugins/"+plugin+"/enabled")):

                    plugin_icon = Context().getUserRoot()+"/plugins/"+plugin+"/icon"
                    
                    if(not os.path.exists(plugin_icon)):
                        plugin_icon = Context().getAppPath()+"/resources/icons/playonlinux16.png"

                    self.addMenuItem(300+self+j, plugin, plugin_icon, self.pluginsmenu)
                    wx.EVT_MENU(self, 300+self.j, self.run_plugin)
                    self.plugin_list.append(plugin)

        if(len(self.plugin_list) > 0):
            self.pluginsmenu.AppendSeparator()

        self.addMenuItem(214,  _("Plugin manager"), "plugins.png", self.pluginsmenu)
        
        self.menubar = wx.MenuBar()
        self.menubar.Append(self.filemenu, _("File"))
        self.menubar.Append(self.displaymenu, _("Display"))
        self.menubar.Append(self.expertmenu, _("Tools"))
        self.menubar.Append(self.optionmenu, _("Settings"))
        self.menubar.Append(self.pluginsmenu, _("Plugins"))
        self.menubar.Append(self.help_menu, "&Help")
                
        self.SetMenuBar(self.menubar)
        
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
        
        # Miscellaneous
        wx.EVT_MENU(self, 216,  self.donate)
        
        
    def drawToolBar(self):
        self.toolbar = self.CreateToolBar(wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize((32,32))
        self.searchbox = wx.SearchCtrl( self.toolbar, 124, style=wx.RAISED_BORDER )
        self.playTool = self.toolbar.AddLabelTool(wx.ID_OPEN, _("Run"), wx.Bitmap(Context().getAppPath()+"/resources/images/toolbar/play.png"))
        self.stopTool = self.toolbar.AddLabelTool(123, _("Close"), wx.Bitmap(Context().getAppPath()+"/resources/images/toolbar/stop.png"))

        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_ADD, _("Install"), wx.Bitmap(Context().getAppPath()+"/resources/images/toolbar/install.png"))
        self.removeTool = self.toolbar_remove = self.toolbar.AddLabelTool(wx.ID_DELETE, _("Remove"), wx.Bitmap(Context().getAppPath   ()+"/resources/images/toolbar/delete.png"))
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(121, _("Configure"), wx.Bitmap(Context().getAppPath()+"/resources/images/toolbar/configure.png"))

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
        
        wx.EVT_MENU(self, wx.ID_OPEN,  self.Run)
        wx.EVT_MENU(self, 123,  self.RKill)

        wx.EVT_MENU(self, wx.ID_ADD,  self.InstallMenu)
        wx.EVT_MENU(self, wx.ID_ABOUT,  self.About)
        wx.EVT_MENU(self,  wx.ID_EXIT,  self.ClosePol)
        wx.EVT_MENU(self,  wx.ID_DELETE,  self.UninstallGame)

        
    def ResizeWindow(self, e):
        self.UpdateGaugePos()
        self.UpdateSearchHackSize()
       
    def UpdateSearchHackSize(self):
        if(self.SpaceHack == True):
            self.dirtyHack.SetLabel("")
            self.dirtyHack.SetSize((50,1))

    def UpdateGaugePos(self):
        if(Context().getOS() == "Mac"):
            hauteur = 2;
        else:
            hauteur = 6;
        self.jauge_update.SetPosition((self.GetSize()[0]-100, hauteur))
        
      
      
        
        
    ## Manage GuiServer Queue
    
    # To save CPU time, we make the SetupWindow timer slower if there are no windows open. We make it faster when a window is opened to get the GUI more responsive
    def changeSetupWindowTimer(self, time):
        if(time != self.SetupWindowTimer_delay):
            self.SetupWindowTimer.Stop()
            self.SetupWindowTimer.Start(time)
            self.SetupWindowTimer_delay = time

    # Each time the timer is called, we decide if we need to change the time, and we read the queue
    def readGuiServerQueue(self, event):
        if(Context().getWindowOpened() == 0):
            self.changeSetupWindowTimer(100)
        else:
            self.changeSetupWindowTimer(10)
            
        queue = GuiServer().getQueue()
    
        while(not queue.isEmpty()):
            self.doGuiTask(queue.getTask())
            queue.shift()
 
    # Do a task
    def doGuiTask(self, data):
        command = data[0]
        scriptPid = data[1]
        
        if(command == "SimpleMessage"):
            Message(data[2])
            GuiServer().getState().release(scriptPid)
            
        if(command == "POL_Die"):
            self.playonlinuxSystem.polDie()
            GuiServer().getState().release(scriptPid)
        
        if(command == "POL_Restart"):
            self.playonlinuxSystem.polRestart()
            GuiServer().getState().release(scriptPid)
            
        if(command == 'POL_System_RegisterPID'):
            Context().registerPid(scriptPid)  
            GuiServer().getState().release(scriptPid)      
        
        if(command == 'POL_SetupWindow_Init'):
           if(len(data) == 6):
                isProtected = data[5] == "TRUE"
                self.windowList[scriptPid] = SetupWindow(title = data[2], scriptPid = scriptPid, topImage = data[3], leftImage = data[4], isProtected = isProtected)
                Context().incWindowOpened() 
                GuiServer().getState().release(scriptPid)   
        
    
        if(command == 'POL_SetupWindow_Close'):
            try:
                self.windowList[scriptPid].Destroy()
                GuiServer().getState().release(scriptPid)   
            except KeyError:
                print "Please use POL_SetupWindow_Init first"
           
        setupWindowCommands = ["POL_SetupWindow_message", "POL_SetupWindow_SetID", "POL_SetupWindow_UnsetID", 
        "POL_SetupWindow_shortcut_list", "POL_SetupWindow_prefix_selector", "POL_SetupWindow_pulsebar", "POL_SetupWindow_question", 
        "POL_SetupWindow_wait", "POL_SetupWindow_wait_bis", "POL_SetupWindow_free_presentation", "POL_SetupWindow_textbox", 
        "POL_SetupWindow_debug", "POL_SetupWindow_textbox_multiline", "POL_SetupWindow_browse", "POL_SetupWindow_download",
        "POL_SetupWindow_menu", "POL_SetupWindow_menu_num", "POL_SetupWindow_checkbox_list", "POL_SetupWindow_icon_menu", "POL_SetupWindow_licence", 
        "POL_SetupWindow_login", "POL_SetupWindow_file", "POL_SetupWindow_pulse", "POL_SetupWindow_set_text"]
        
        if(command in setupWindowCommands):
            
            arguments = data[2:]
            
            try:
                setupWindowObject = self.windowList[scriptPid]
            except KeyError:
                print "Please use POL_SetupWindow_Init first"
            else: 
                try:
                    setupWindowFunction = getattr(setupWindowObject, command)
                except AttributeError:
                    print 'Function not found "%s" (%s)' % (command, arguments)
                else:
                    try:
                        setupWindowFunction(*arguments)
                    except TypeError, e:
                        print 'Error: %s (%s)' % (e, arguments)
        
           
           
    def TimerAction(self, event):
        self.StatusRead()
        # We read shortcut folder to see if it has to be rescanned
        currentShortcuts = os.path.getmtime(Context().getUserRoot()+"/shortcuts")
        currentIcons = os.path.getmtime(Context().getUserRoot()+"/icones/32")
        if(currentShortcuts != self.Timer_LastShortcutList or currentIcons != self.Timer_LastIconList):
            self.Reload(self)
            self.Timer_LastShortcutList = currentShortcuts
            self.Timer_LastIconList = currentIcons
            
    def MgrAddPage(self):
        try:
            self.LoadSize = int(self.playonlinuxSettings.getSetting("PANEL_SIZE"))
        except:
            self.LoadSize = 150

        try:
            self.LoadPosition = self.playonlinuxSettings.getSetting("PANEL_POSITION")
        except:
            self.LoadPosition = "LEFT"

        if(self.LoadSize < 20):
            self.LoadSize = 20
        if(self.LoadSize > 1000):
            self.LoadSize = 1000


        if(self.LoadPosition == "LEFT"):
            self._mgr.AddPane(self.leftPanel, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Left().BestSize((self.LoadSize,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
        else:
            self._mgr.AddPane(self.leftPanel, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Right().BestSize((self.LoadSize,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
        self.leftPanel.Show()

        self._mgr.Update()

    def displayMen(self, event):
        self.playonlinuxSettings.setSetting("PANEL_POSITION","LEFT")
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
            wx.MessageBox(self.alert, Context().getAppName())

    def RMBInGameList(self, event):
        self.GameListPopUpMenu = wx.Menu()

        self.ConfigureWine = wx.MenuItem(self.GameListPopUpMenu, 230, _("Configure Wine"))
        self.ConfigureWine.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/run.png"))
        self.GameListPopUpMenu.AppendItem(self.ConfigureWine)

        self.RegistryEditor = wx.MenuItem(self.GameListPopUpMenu, 231, _("Registry Editor"))
        self.RegistryEditor.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/regedit.png"))
        self.GameListPopUpMenu.AppendItem(self.RegistryEditor)

        self.GotoAppDir = wx.MenuItem(self.GameListPopUpMenu, 232, _("Open the application's directory"))
        self.GotoAppDir.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/folder-wine.png"))
        self.GameListPopUpMenu.AppendItem(self.GotoAppDir)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 236, _("Read the manual"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/manual.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 233, _("Set the icon"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/change_icon.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 234, _("Remove"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/delete.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 235, _("Close this application"))
        self.ChangeIcon.SetBitmap(wx.Bitmap(Context().getUserRoot()+"/resources/images/menu/media-playback-stop.png"))
        self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

        self.PopupMenu(self.GameListPopUpMenu, event.GetPoint())
        
        # Register events
        wx.EVT_MENU(self, 230, self.RWineConfigurator)
        wx.EVT_MENU(self, 231, self.RRegistryEditor)
        wx.EVT_MENU(self, 232, self.GoToAppDir)
        wx.EVT_MENU(self, 233, self.ChangeIcon)
        wx.EVT_MENU(self, 234, self.UninstallGame)
        wx.EVT_MENU(self, 235, self.RKill)
        wx.EVT_MENU(self, 236, self.ReadMe)
        

    def addMenuItem(self, id, title, icon, menu):
        if(icon != None):
            item = wx.MenuItem(menu, id, _(title))
            os.chdir(Context().getAppPath()+"/resources/images/menu/")
            
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
        if(os.path.exists(Context().getUserRoot()+"/configurations/manuals/"+game_exec)):
            playonlinux.POL_Open(Context().getUserRoot()+"/configurations/manuals/"+game_exec)
        else:
            wx.MessageBox(_("No manual found for {0}").format(game_exec), Context().getAppName())

    def RRegistryEditor(self, event):
        self.RConfigure(_("Registry Editor"), "nothing")

    def run_plugin(self, event):
        game_exec = self.GetSelectedProgram()
        plugin=self.plugin_list[event.GetId()-300]
        try :
            os.system("bash \""+Context().getUserRoot()+"/plugins/"+plugin+"/scripts/menu\" \""+game_exec+"\"&")
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

        self.playonlinuxSettings.setSetting("ICON_SIZE",str(self.iconSize))
        self.appList.SetImageList(self.imagesEmpty)
        self.images.Destroy()
        self.images = wx.ImageList(self.iconSize, self.iconSize)
        self.appList.SetImageList(self.images)


        self.Reload(self)

    def OpenIrc(self, event):
        self.irc = ircgui.IrcClient(self)
        self.irc.Center(wx.BOTH)
        self.irc.Show(True)

    def UpdateGIT(self, event):
        os.system("bash \""+Context().getUserRoot()+"/bash/update_git\"&")


    def GoToAppDir(self, event):
        self.game_exec = self.GetSelectedProgram()
        playonlinux.open_folder(self.game_exec)

    def ChangeIcon(self, event):
        self.IconDir = Context().getHomeDir()+"/.local/share/icons/"
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
        game_exec = self.GetSelectedProgram().getName()
        
        self.read = open(Context().getUserRoot()+"shortcuts/"+game_exec,"r").readlines()
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
        self.menuGaucheAddTitle("pol_title", Context().getAppName(), i)
        i+=1
        self.addLinkToLeftMenu("pol_prgm_install", _("Install a program"), i,Context().getAppPath()+"/resources/images/menu/add.png",self.InstallMenu)
        i+=1
        self.addLinkToLeftMenu("pol_prgm_settings", _("Settings"), i,Context().getAppPath()+"/resources/images/menu/settings.png",self.Options)
        i+=1
        self.addLinkToLeftMenu("pol_prgm_messenger", _("Messenger"), i,Context().getAppPath()+"/resources/images/menu/people.png",self.OpenIrc)
        if(os.path.exists(Context().getAppPath()+"/.git/")):
            i+=1
            self.addLinkToLeftMenu("pol_git", _("Update GIT"), i,Context().getAppPath()+"/resources/images/menu/update_git.png",self.UpdateGIT)

        if(shortcut != None):
            i+=2
            self.menuGaucheAddTitle("prgm_title", shortcut, i)
            i+=1
            self.addLinkToLeftMenu("pol_prgm_run", _("Run"), i,Context().getAppPath()+"/resources/images/menu/media-playback-start.png",self.Run)
            i+=1
            self.addLinkToLeftMenu("pol_prgm_kill", _("Close"), i,Context().getAppPath()+"/resources/images/menu/media-playback-stop.png",self.RKill)
            i+=1
            self.addLinkToLeftMenu("pol_prgm_rundebug", _("Debug"), i,Context().getAppPath()+"/resources/images/menu/bug.png",self.RunDebug)
            i+=1
            self.addLinkToLeftMenu("pol_prgm_configure", _("Configure"), i,Context().getAppPath()+"/resources/images/menu/run.png",self.Configure)
            i+=1
            self.addLinkToLeftMenu("pol_prgm_shortcut", _("Create a shortcut"), i,Context().getAppPath()+"/resources/images/menu/shortcut.png",self.Package)
            i+=1
            self.addLinkToLeftMenu("pol_prgm_adddir", _("Open the directory"), i,Context().getAppPath()+"/resources/images/menu/folder-wine.png",self.GoToAppDir)

            if(os.path.exists(Context().getUserRoot()+"/configurations/manuals/"+shortcut)):
                i+=1
                self.addLinkToLeftMenu("pol_prgm_readme", _("Read the manual"), i,Context().getAppPath()+"/resources/images/menu/manual.png",self.ReadMe)

            i+=1
            self.addLinkToLeftMenu("pol_prgm_uninstall", _("Uninstall"), i,Context().getAppPath()+"/resources/images/menu/window-close.png",self.UninstallGame)


            self.linksfile = Context().getUserRoot()+"/configurations/links/"+shortcut
            if(os.path.exists(self.linksfile)):
                self.linksc = open(self.linksfile,"r").read().split("\n")
                for line in self.linksc:
                    if("|" in line):
                        line = line.split("|")
                        i+=1
                        if("PROFILEBUTTON/" in line[0]):
                            line[0] = line[0].replace("PROFILEBUTTON/","")

                        self.addLinkToLeftMenu("url_"+str(i), line[0], i,Context().getUserRoot()+"/resources/images/menu/star.png",None,line[1])

            icon = Context().getUserRoot()+"/icones/full_size/"+shortcut

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
                        self.menuBitmap = wx.StaticBitmap(self.leftPanel, id=-1, bitmap=self.bitmap, pos=(left_pos,20+(i+2)*20))
                except:
                    pass

    def menuGaucheAddTitle(self,id,text,pos):
        self.menuElem[id] = wx.StaticText(self.leftPanel, -1, text,pos=(5,5+pos*20))
        self.menuElem[id].SetForegroundColour((0,0,0)) # For dark themes
        self.menuElem[id].SetFont(UIHelper().getFontTitle())


    def addLinkToLeftMenu(self,id,text,pos,image,evt,url=None):
        if(os.path.exists(image)):
            menu_icone = image
        else:
            menu_icone = Context().getAppPath()+"/etc/playonlinux.png"

        try:
            self.bitmap = wx.Image(menu_icone)
            self.bitmap.Rescale(16,16,wx.IMAGE_QUALITY_HIGH)
            self.bitmap = self.bitmap.ConvertToBitmap()
            self.menuImage[id] = wx.StaticBitmap(self.leftPanel, id=-1, bitmap=self.bitmap, pos=(10,15+pos*20))

        except:
            pass

        if(url == None):
            self.menuElem[id] = wx.HyperlinkCtrl(self.leftPanel, 10000+pos, text, "", pos=(35,15+pos*20))
        else:
            self.menuElem[id] = wx.HyperlinkCtrl(self.leftPanel, 10000+pos, text, url, pos=(35,15+pos*20))

        self.menuElem[id].SetNormalColour(wx.Colour(0,0,0))
        self.menuElem[id].SetVisitedColour(wx.Colour(0,0,0))
        self.menuElem[id].SetHoverColour(wx.Colour(100,100,100))

        if(evt != None):
            wx.EVT_HYPERLINK(self, 10000+pos, evt)

    def donate(self, event):
        if(Context().getOS() == "Mac"):
            webbrowser.open("http://www.playonmac.com/en/donate.html")
        else:
            webbrowser.open("http://www.playonlinux.com/en/donate.html")

    def Reload(self, event):
        self.games = os.listdir(Context().getUserRoot()+"shortcuts/")
        self.games.sort()
        
        try:
            self.games.remove(".DS_Store")
        except:
            pass
            
        self.appList.DeleteAllItems()
        self.images.RemoveAll()
        root = self.appList.AddRoot("")
        self.i = 0
        if(self.iconSize <= 32):
            self.iconFolder = "32";
        else:
            self.iconFolder = "full_size";
        for game in self.games: #METTRE EN 32x32
            if(self.searchbox.GetValue().encode("utf-8","replace").lower() in game.lower()):
                if(not os.path.isdir(Context().getUserRoot()+"/shortcuts/"+game)):
                    if(os.path.exists(Context().getUserRoot()+"/icones/"+self.iconFolder+"/"+game)):
                         file_icone = Context().getUserRoot()+"/icones/"+self.iconFolder+"/"+game
                    else:
                        file_icone = Context().getAppPath()+"/etc/playonlinux.png"

                    try:
                        self.bitmap = wx.Image(file_icone)
                        self.bitmap.Rescale(self.iconSize,self.iconSize,wx.IMAGE_QUALITY_HIGH)
                        self.bitmap = self.bitmap.ConvertToBitmap()
                        self.images.Add(self.bitmap)
                    except:
                        pass
                    
                    item = self.appList.AppendItem(root, game, self.i)
                    self.i += 1
        self.generate_menu(None)

        if(Context().getOS() == "Mac"):
            self.playTool.Enable(False)
            self.stopTool.Enable(False)
            self.removeTool.Enable(False)


    def RConfigure(self, function_to_run, firstargument):
        """Starts polconfigurator remotely."""
        game_exec = self.GetSelectedProgram()
        if(game_exec != ""):
            os.system("bash \""+Context().getAppPath()+"/bash/polconfigurator\" \""+game_exec+"\" \""+function_to_run+"\" \""+firstargument+"\"&")
        else:
            wx.MessageBox(_("Please select a program."), Context().getAppName())


    def Options(self, event):
        onglet=event.GetId()
        try:
            self.optionFrame.SetFocus()
        except:
            self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(Context().getAppName()), 2)
            if(onglet == 211):
                self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(Context().getAppName()), 0)
            if(onglet == 214):
                self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(Context().getAppName()), 1)
            self.optionFrame.Center(wx.BOTH)
            self.optionFrame.Show(True)

    def killall(self, event):
        PrivateGUIScript("killall").runBackground()

    def Executer(self, event):
        PrivateGUIScript("localScript").runBackground()

    def BugReport(self, event):
        try:
            self.debugFrame.Show()
            self.debugFrame.SetFocus()
        except:
            self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(Context().getAppName()))
            self.debugFrame.Center(wx.BOTH)
            self.debugFrame.Show()


    def POLOnline(self, event):
        os.system("bash \""+Context().getAppPath()+"/bash/playonlinux_online\" &")

    def PCCd(self, event):
        os.system("bash \""+Context().getAppPath()+"/bash/read_pc_cd\" &")

    def PolShell(self, event):
        PrivateGUIScript("POLShell").runBackground()
        #print "Test"
        
    def Configure(self, event):
        game_exec = self.GetSelectedProgram()
        try:
            self.configureFrame.Show(True)
            self.configureFrame.SetFocus()
            if(game_exec != ""):
                self.configureFrame.change_program(game_exec,False)

        except:
            if(game_exec == ""):
                self.configureFrame = configure.MainWindow(self, -1, _("{0} configuration").format(Context().getAppName()),"default",True)
            else:
                self.configureFrame = configure.MainWindow(self, -1, _("{0} configuration").format(Context().getAppName()),game_exec.decode("utf-8","replace"),False)


            self.configureFrame.Center(wx.BOTH)
            self.configureFrame.Show(True)

        #os.system("bash \""+Context().getUserRoot()+"/bash/polconfigurator\" \""+game_exec+"\"&")

    def Package(self, event):
        game_exec = self.GetSelectedProgram()
        os.system("bash \""+Context().getAppPath()+"/bash/make_shortcut\" \""+game_exec.encode("utf-8","replace")+"\"&")

    def UninstallGame(self, event):
        shortcutToUninstall = self.GetSelectedProgram()
        shortcutToUninstall.uninstall()

    def InstallMenu(self, event):
        try:
            self.installFrame.Show(True)
            self.installFrame.SetFocus()
        except:
            self.installFrame = install.InstallWindow(self, -1, _('{0} install menu').format(Context().getAppName()))
            self.installFrame.Center(wx.BOTH)
            self.installFrame.Show(True)

    def WineVersion(self, event):
        try:
            self.wversion.Show()
            self.wversion.SetFocus()
        except:
            self.wversion = wver.MainWindow(None, -1, _('{0} wine versions manager').format(Context().getAppName()))
            self.wversion.Center(wx.BOTH)
            self.wversion.Show(True)

    def GetSelectedProgram(self):
        selectedName = self.appList.GetItemText(self.appList.GetSelection()).encode("utf-8","replace")
        if(selectedName == ""):
            raise ErrNoProgramSelected
            
        return Shortcut(Context(), selectedName)
        
    def Run(self, event, s_debug=False):
        selectedProgram = self.GetSelectedProgram()
        game_exec = self.GetSelectedProgram().getName()
        game_prefix = self.GetSelectedProgram().getPrefix()

        if(s_debug == False):
            selectedProgram.setDebug(False)

        if(game_prefix.exists()):
            if(game_exec != ""):
                if(selectedProgram.isDebug()):
                    try:
                        self.debugFrame.analyseReal(0, game_prefix.getName())
                        self.debugFrame.Show()
                        self.debugFrame.SetFocus()
                    except:
                        self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(Context().getAppName()),game_prefix.getName(),0)
                        self.debugFrame.Center(wx.BOTH)
                        self.debugFrame.Show()

                selectedProgram.runPoll()
            else:
                wx.MessageBox(_("Please select a program."), Context().getAppName())
        else:
            wx.MessageBox(_("The virtual drive associated with {0} ({1}) does no longer exists.").format(game_exec, game_prefix.getName()), Context().getAppName())

    def RunDebug(self, event):
        game_exec = self.GetSelectedProgram()
        game_prefix = playonlinux.getPrefix(game_exec)
        playonlinux.SetDebugState(game_exec, True)
        self.Run(self, True)


    def saveWindowParametersToConfig(self):
        self.SizeToSave = self.GetSize();
        self.PositionToSave = self.GetPosition();
        # Save size and position
        self.playonlinuxSettings.setSetting("MAINWINDOW_WIDTH",str(self.SizeToSave[0]))
        self.playonlinuxSettings.setSetting("MAINWINDOW_HEIGHT",str(self.SizeToSave[1] - UIHelper().addMacOffset(56)))
        self.playonlinuxSettings.setSetting("MAINWINDOW_X",str(self.PositionToSave[0]))
        self.playonlinuxSettings.setSetting("MAINWINDOW_Y",str(self.PositionToSave[1]))
        
    def savePanelParametersToConfig(self):
        # Very ugly, need to be fixed
        self._mgr.UnInit()
            
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

        self.playonlinuxSettings.setSetting("PANEL_SIZE",str(self.mySize))
        self.playonlinuxSettings.setSetting("PANEL_POSITION",str(self.myPosition))
        
    def ClosePol(self, event):
        if(self.playonlinuxSettings.getSetting("DONT_ASK_BEFORE_CLOSING") == "TRUE" or Question(_('Are you sure you want to close all [APP] Windows?')).getAnswer()):
            self.saveWindowParametersToConfig()
            self.savePanelParametersToConfig()
            self.playonlinuxSystem.polDie()
            
        return None

    def About(self, event):
        self.aboutBox = wx.AboutDialogInfo()
        if(Context().getOS() == "Linux"):
            self.aboutBox.SetIcon(wx.Icon(Context().getAppPath()+"/resources/icons/playonlinux.png", wx.BITMAP_TYPE_ANY))

        
        self.aboutBox.SetName(Context().getAppName())
        self.aboutBox.SetVersion(Context().getAppVersion())
        self.aboutBox.SetDescription(_("Run your Windows programs on "+Context().getOS()+" !"))
        self.aboutBox.SetCopyright("© 2007-2013 "+_("PlayOnLinux and PlayOnMac team\nUnder GPL licence version 3"))
        self.aboutBox.AddDeveloper(_("Developer and Website: ")+"Tinou (Pâris Quentin), MulX (Petit Aymeric)")
        self.aboutBox.AddDeveloper(_("Scriptors: ")+"GNU_Raziel")
        self.aboutBox.AddDeveloper(_("Packager: ")+"MulX (Petit Aymeric), Tinou (Pâris Quentin)")
        self.aboutBox.AddDeveloper(_("Icons:")+"Faenza-Icons http://tiheum.deviantart.com/art/Faenza-Icons-173323228")
        self.aboutBox.AddDeveloper(_("The following people contributed to this program: ")+"kiplantt, Salvatos, Minchul")
        self.aboutBox.AddTranslator(_("Translations:"))
        self.aboutBox.AddTranslator(_("Read TRANSLATORS file"))

        if(Context().getOS() == "Mac"):
            self.aboutBox.SetWebSite("http://www.playonmac.com")
        else:
            self.aboutBox.SetWebSite("http://www.playonlinux.com")
        wx.AboutBox(self.aboutBox)
