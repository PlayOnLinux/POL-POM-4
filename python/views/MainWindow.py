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

# Views
from views.UIHelper import UIHelper
from views.PolAbout import PolAbout
from views.Question import Question

# from views.SetupWindow import SetupWindow
# from views.Question import Question
# from views.Message import Message

from services.ConfigService import ConfigService
from services.Environment import Environment

from patterns.Observer import Observer
from patterns.Observable import Observable

#, install, options, wine_versions as wver, sp, configure, debug, gui_server
#import irc as ircgui

# Exceptions
class ErrNoProgramSelected(Exception):
   def __str__(self):
      return repr(_("You must select a program"))


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
           
class InstalledApps(wx.TreeCtrl, Observer, Observable):
    def __init__(self, frame, controller):
        wx.TreeCtrl.__init__(self, frame, 105, style = wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        Observer.__init__(self)
        Observable.__init__(self)
        
        self.frame = frame
        self.controller = controller
        self.SetSpacing(0)
        self.SetIndent(5)
        self.config = ConfigService()
        self.iconSize = self.config.getIntSetting("ICON_SIZE", default = 32)
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
        self.config.setSetting("ICON_SIZE",str(size))
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
        
class PanelManager(wx.aui.AuiManager):
    def __init__(self, frame):
        wx.aui.AuiManager.__init__(self, frame)
        self.config = ConfigService()
        
    def _getPerspectiveName(self):
        name = self.SavePerspective().split("=")
        name = name[1].split(";")
        name = name[0]
        return name 

    def getPerspective(self):
        return self.SavePerspective().replace(self._getPerspectiveName(),"PERSPECTIVE_NAME")
        
    def savePosition(self):
        self.config.setSetting("PANEL_PERSPECTIVE", self.getPerspective())
        
    def restorePosition(self):
        self.Update()
        setting = self.config.getSetting("PANEL_PERSPECTIVE")
        if(setting != ""):
            self.LoadPerspective(setting.replace("PERSPECTIVE_NAME",self._getPerspectiveName()))
        self.Update()
         
    def AddPane(self, data, settings):
        wx.aui.AuiManager.AddPane(self, data, settings)
        
    def Destroy(self):
        self.savePosition()
        
                  
class MenuPanel(wx.Panel, Observer):
    def __init__(self, frame, controller, id = -1):
        wx.Panel.__init__(self, frame, id)   
        Observer.__init__(self)
        self.controller = controller
        self.frame = frame
        self.uiHelper = UIHelper()
        self.config = ConfigService()
        self.env = Environment()
        self.menuElems = []
        self.Show()
        self.currentPosition = 0
    
    def addTitle(self, text):
        if(self.currentPosition != 0):
            self.currentPosition += 1
        elem = wx.StaticText(self, -1, text, pos=(5,5+self.currentPosition*20))
        elem.SetForegroundColour((0,0,0))
        elem.SetFont(self.uiHelper.getFontTitle())    
        self.menuElems.append(elem)
        self.currentPosition += 1

    def addLink(self, text, id, image, url = None):
        self.menuElems.append(wx.StaticBitmap(self, id = -1, bitmap = self.uiHelper.getBitmap(image, 16), pos = (10,15+self.currentPosition*20)))

        if(url == None):
            url = ""
        
        elem = wx.HyperlinkCtrl(self, id, text, url, pos=(35,15+self.currentPosition*20))
        elem.SetNormalColour(wx.Colour(0,0,0))
        elem.SetVisitedColour(wx.Colour(0,0,0))
        elem.SetHoverColour(wx.Colour(100,100,100))
        self.menuElems.append(elem)
        self.currentPosition += 1
        
    def destroyContent(self):
        for c in self.menuElems:
            c.Destroy()
            
        try:
            self.menuBitmap.Destroy()
        except AttributeError:
            pass
            
        self.menuElems = []
        self.currentPosition = 0
        
    def generateContent(self, selectedShortcut = None, hasManual = False, links = {}, icon = None):
        self.destroyContent()
        self.addTitle(self.config.getAppName())
        self.addLink(_("Install a program"), 10001, "menu/add.png")
        self.addLink(_("Settings"), 10002, "menu/settings.png")
        self.addLink(_("Messenger"), 10003, "menu/people.png")
        
        if(self.env.isGIT()):
            self.addLink(_("Update GIT"), 10004, "menu/update_git.png")

        if(selectedShortcut != None):       
            self.addTitle(selectedShortcut)
            self.addLink(_("Run"), 10006, "menu/media-playback-start.png")
            self.addLink(_("Close"), 10007,"menu/media-playback-stop.png")
            self.addLink(_("Debug"), 10008,"menu/bug.png")
            self.addLink(_("Configure"), 10009,"menu/run.png")
            self.addLink(_("Create a shortcut"), 10010,"menu/shortcut.png")
            self.addLink(_("Open the directory"), 10011,"menu/folder-wine.png")
            if(hasManual):
                self.addLink(_("Read the manual"), 10012,"menu/manual.png")
            self.addLink(_("Uninstall"), 10013,"menu/window-close.png")

            
            for name, url in links:
                self.addLink(line[0], -1, "menu/star.png", url)
                
            if(icon != None):
                bitmap = self.uiHelper.getBitmap(icon, 48)
                self.menuBitmap = wx.StaticBitmap(self, id=-1, bitmap = bitmap, pos=((self.GetSize()[0]-48)/2,20+(self.currentPosition+1)*20))
         
            
    def notify(self):
        self.generateContent()
    

class Toolbar(wx.ToolBar, Observer):
    def __init__(self, frame):
        wx.ToolBar.__init__(self, frame, style = wx.TB_TEXT)
        Observer.__init__(self)
        
        self.uiHelper = UIHelper()
        
        self.SetToolBitmapSize((32,32))
        self.searchbox = wx.SearchCtrl( self, 124, style=wx.RAISED_BORDER )
        self.playTool = self.AddLabelTool(wx.ID_OPEN, _("Run"), self.uiHelper.getBitmap("toolbar/play.png"))
        self.stopTool = self.AddLabelTool(123, _("Close"), self.uiHelper.getBitmap("toolbar/stop.png"))

        self.AddSeparator()
        self.AddLabelTool(wx.ID_ADD, _("Install"), self.uiHelper.getBitmap("toolbar/install.png"))
        self.removeTool = self.AddLabelTool(wx.ID_DELETE, _("Remove"), self.uiHelper.getBitmap("toolbar/delete.png"))
        self.AddSeparator()
        self.AddLabelTool(121, _("Configure"), self.uiHelper.getBitmap("toolbar/configure.png"))

        self.AddStretchableSpace()
        """ FIXME linux ?
            self.toolbar.AddControl( self.searchbox ) 
            self.searchbox.SetDescriptiveText(_("Search"))
        """
    
        self.AddControl( self.searchbox , _("Search")) 
   
    def enableIcons(self):
        self.playTool.Enable(True)
        self.stopTool.Enable(True)
        self.removeTool.Enable(True)
        
    # Observer event
    def notify(self):
        self.playTool.Enable(False)
        self.stopTool.Enable(False)
        self.removeTool.Enable(False)
        
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
        
class MainWindow(wx.Frame):
    def __init__(self, controller, id = -1):
        self.configService = ConfigService()
        self.env = Environment()
        self.uiHelper = UIHelper()
        self.controller = controller
        
        wx.Frame.__init__(self, None, id, self.configService.getAppName(), size = (515,450))
        self.SetIcon(self.uiHelper.getIcon("playonlinux.png"))
        
        # Window size
        self.SetMinSize((400,400))
        self.windowWidth = self.configService.getIntSetting("MAINWINDOW_WIDTH", default = 450)
        self.windowHeight = self.configService.getIntSetting("MAINWINDOW_HEIGHT", default = 450)
        self.SetSize((self.windowWidth,self.windowHeight))
        
        # Window position
        self.windowx = self.configService.getIntSetting("MAINWINDOW_X", default = 30)
        self.windowy = self.configService.getIntSetting("MAINWINDOW_Y", default = 30)
        self.screen_width = wx.Display().GetGeometry()[2]
        self.screen_height = wx.Display().GetGeometry()[3]

        if(self.screen_width >= self.windowx and self.screen_height >= self.windowy):
            self.SetPosition((self.windowx, self.windowy))
        else:
            self.Center(wx.BOTH)
            
             
        # Manage updater
        #self.updater = POLWeb()
        #self.updater.start()
    
    
        
        self._appList = InstalledApps(self, self.controller)
        self._menuPanel = MenuPanel(self, self.controller)
        
        # Left menu
        self._mgr = PanelManager(self)
        self._mgr.AddPane(self._appList, wx.CENTER)
        self._mgr.AddPane(self._menuPanel, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Left().BestSize((200,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
        self._mgr.restorePosition()     
    
        # Toolbar
        self._toolbar = Toolbar(self)
        self.SetToolBar(self._toolbar)
        self._toolbar.Realize()
        
        # The toolbar and the left panel observes the app list change
        self._appList.register(self._toolbar)
        self._appList.register(self._menuPanel)
        
        # Menubar
        self._menuBar = MenuBar(self.controller, self)
        self.SetMenuBar(self._menuBar)
        
        
        # Status bar
        self.drawStatusBar()
        





        
        # Events
        wx.EVT_TEXT(self, 124,  self.eventSearch)
        
        wx.EVT_TREE_SEL_CHANGED(self, 105, self.eventSelect)
        wx.EVT_CLOSE(self, self.eventClosePol)
        
        wx.EVT_TREE_ITEM_ACTIVATED(self, 105, self.eventRunProgram) 
        
        
        # Display
        wx.EVT_MENU(self, 501,  self.changeIconSize)
        wx.EVT_MENU(self, 502,  self.changeIconSize)
        wx.EVT_MENU(self, 503,  self.changeIconSize)
        wx.EVT_MENU(self, 504,  self.changeIconSize)

        # Expert
        wx.EVT_MENU(self, 107,  self.WineVersion)
        wx.EVT_MENU(self, 108,  self.scriptRunLocalScript)
        wx.EVT_MENU(self, 109,  self.eventPlayOnLinuxConsole)
        wx.EVT_MENU(self, 110,  self.BugReport)
        wx.EVT_MENU(self, 111,  self.OpenIrc)
        wx.EVT_MENU(self, 112,  self.POLOnline)
        wx.EVT_MENU(self, 113,  self.PCCd)
        wx.EVT_MENU(self, 115,  self.scriptKillall)
        wx.EVT_MENU(self, 121,  self.Configure)
        wx.EVT_MENU(self, 122,  self.Package)

        
        #Options
        wx.EVT_MENU(self, 210,  self.Options)
        wx.EVT_MENU(self, 211,  self.Options)
        wx.EVT_MENU(self, 212,  self.Options)
        wx.EVT_MENU(self, 213,  self.Options)
        wx.EVT_MENU(self, 214,  self.Options)
        wx.EVT_MENU(self, 215,  self.Options)
        
        # Miscellaneous    
        wx.EVT_MENU(self, wx.ID_ABOUT,  self.eventAbout)
        wx.EVT_MENU(self,  wx.ID_EXIT,  self.eventClosePol)
        wx.EVT_MENU(self, wx.ID_OPEN,  self.eventRunProgram)
        wx.EVT_MENU(self, 216,  self.eventDonate)
    
        
         

        #if(self.env.getOS() == "Mac"):
            #self.Bind(wx.EVT_MENU, self.Options, prefItem)
        # Program list event
        #wx.EVT_TREE_SEL_CHANGED(self, 105, self.Select)

    
        # wx.EVT_MENU(self, 123,  self.RKill)
  
        # wx.EVT_MENU(self, wx.ID_ADD,  self.InstallMenu)
    
        #wx.EVT_MENU(self,  wx.ID_DELETE,  self.UninstallGame)
      
        # PlayOnLinux main timer
        #self.timer = wx.Timer(self, 1)
        #self.Bind(wx.EVT_TIMER, self.TimerAction, self.timer)
        #self.timer.Start(1000)
  
        # SetupWindow timer. The server is in another thread and GUI must be run from the main thread
        #self.SetupWindowTimer = wx.Timer(self, 2)
        #self.Bind(wx.EVT_TIMER, self.readGuiServerQueue, self.SetupWindowTimer)
        #self.SetupWindowTimer.Start(100)
        #self.SetupWindowTimer_delay = 100

        #Pop-up menu for game list: beginning
        #wx.EVT_TREE_ITEM_MENU(self, 105, self.RMBInGameList)

        #self.Bind(wx.EVT_SIZE, self.eventResizeWindow)

     
    def drawStatusBar(self):
        self.statusBar = wx.StatusBar(self, -1 )
        self.statusBar.SetFieldsCount(2)
        self.statusBar.SetStatusWidths([self.GetSize()[0], -1])
        self.statusBar.SetStatusText("", 0)

        self.jaugeUpdate = wx.Gauge(self.statusBar, -1, 100, (self.GetSize()[0]-100, UIHelper().updateJaugeMarginTop()), size=(100,16))
        self.jaugeUpdate.Pulse()
        self.jaugeUpdate.Hide()
        self.SetStatusBar(self.statusBar)
        
        
    def eventResizeWindow(self, e):
        self.jaugeUpdate.SetPosition((self.GetSize()[0]-100, UIHelper().updateJaugeMarginTop()))
                
      
        
        
    ## Manage GuiServer Queue
    
    # To save CPU time, we make the SetupWindow timer slower if there are no windows open. We make it faster when a window is opened to get the GUI more responsive
    def changeSetupWindowTimer(self, time):
        if(time != self.SetupWindowTimer_delay):
            self.SetupWindowTimer.Stop()
            self.SetupWindowTimer.Start(time)
            self.SetupWindowTimer_delay = time

    # Each time the timer is called, we decide if we need to change the time, and we read the queue
    def TimerAction(self, event):
        #self.StatusRead()
       return None
        # We read shortcut folder to see if it has to be rescanned
        
        
            
    def StatusRead(self):
        self.statusBar.SetStatusText(self.updater.sendToStatusBarStr, 0)
        if(self.updater.Gauge == True):
            perc = self.updater.perc
            if(perc == -1):
                self.jaugeUpdate.Pulse()
            else:
                try:
                    self.installFrame.percentageText.SetLabel(str(perc)+" %")
                except:
                    pass
                self.jaugeUpdate.SetValue(perc)
            self.jaugeUpdate.Show()
        else:
            self.jaugeUpdate.Hide()

        if(self.updater.updating == True):
            self.statusBar.Show()
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
            self.statusBar.Hide()
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
        

    
        
    def RWineConfigurator(self, event):
        self.RConfigure(_("Configure Wine"), "nothing")

    def RKill(self, event):
        self.RConfigure(_("KillApp"), "nothing")

    def ReadMe(self, event):
        game_exec = self.getSelectedShortcut()
        if(os.path.exists(Context().getUserRoot()+"/configurations/manuals/"+game_exec)):
            playonlinux.POL_Open(Context().getUserRoot()+"/configurations/manuals/"+game_exec)
        else:
            wx.MessageBox(_("No manual found for {0}").format(game_exec), Context().getAppName())

    def RRegistryEditor(self, event):
        self.RConfigure(_("Registry Editor"), "nothing")

    def run_plugin(self, event):
        game_exec = self.getSelectedShortcut()
        plugin=self.plugin_list[event.GetId()-300]
        try :
            os.system("bash \""+Context().getUserRoot()+"/plugins/"+plugin+"/scripts/menu\" \""+game_exec+"\"&")
        except :
            pass

    def changeIconSize(self, event):
        iconEvent = event.GetId()

        if(iconEvent == 501):
            self.iconSize = 16
        if(iconEvent == 502):
            self.iconSize = 24
        if(iconEvent == 503):
            self.iconSize = 32
        if(iconEvent == 504):
            self.iconSize = 48

        self.playonlinuxSettings.setSetting("ICON_SIZE",str(self.iconSize))
        self.writeShortcutsToWidget(forceRefresh = True)

    def OpenIrc(self, event):
        self.irc = ircgui.IrcClient(self)
        self.irc.Center(wx.BOTH)
        self.irc.Show(True)

    def UpdateGIT(self, event):
        os.system("bash \""+Context().getUserRoot()+"/bash/update_git\"&")


    def GoToAppDir(self, event):
        self.game_exec = self.getSelectedShortcut()
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



    



    




    def RConfigure(self, function_to_run, firstargument):
        """Starts polconfigurator remotely."""
        game_exec = self.getSelectedShortcut()
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

    def scriptKillall(self, event):
        PrivateGUIScript("killall").start()

    def scriptRunLocalScript(self, event):
        PrivateGUIScript("localScript").start()

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


        #print "Test"
        
    def Configure(self, event):
        game_exec = self.getSelectedShortcut()
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
        game_exec = self.getSelectedShortcut()
        os.system("bash \""+Context().getAppPath()+"/bash/make_shortcut\" \""+game_exec.encode("utf-8","replace")+"\"&")

    def UninstallGame(self, event):
        shortcutToUninstall = self.getSelectedShortcut()
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

    
        
  






    # UI events 
    def eventSearch(self, event):
        self._appList.setSearchFilter(self.searchbox.GetValue().lower())
        self._appList.refresh()
    
    def eventAbout(self, event):
       self.aboutWindow = PolAbout()
       self.aboutWindow.show()
     
    def eventSelect(self, event):    
        self.controller.selectShortcut(self._menuPanel, self._appList.getSelectedShortcut())
        self._toolbar.enableIcons()
    
    def eventDonate(self, event):
        self.controller.donate()
           
    def eventClosePol(self, event):
        if(self.configService.getSetting("DONT_ASK_BEFORE_CLOSING") == "TRUE" or Question(_('Are you sure you want to close all [APP] Windows?')).getAnswer()):
            self.Destroy()
            self.controller.destroy()  
            
    def eventRunProgram(self, event):
        self.controller.runProgram(self._appList.getSelectedShortcut())
           
    def eventPlayOnLinuxConsole(self, event):
        self.controller.startPlayOnLinuxConsole()
             
    # Getters
    def getAppList(self):
        return self._appList
            
    def getToolbar(self):
        return self._toolbar
    
    def getMenuBar(self):
        return self._menuBar
        
    def getMenuPanel(self):
        return self._menuPanel  
        
    # Closing PlayOnLinux
    def saveWindowParametersToConfig(self):
        self.sizeToSave = self.GetSize();
        self.positionToSave = self.GetPosition();
        # Save size and position
        self.configService.setSetting("MAINWINDOW_WIDTH",str(self.sizeToSave[0]))
        self.configService.setSetting("MAINWINDOW_HEIGHT",str(self.sizeToSave[1] - self.uiHelper.addMacOffset(56)))
        self.configService.setSetting("MAINWINDOW_X",str(self.positionToSave[0]))
        self.configService.setSetting("MAINWINDOW_Y",str(self.positionToSave[1]))
                
    def Destroy(self):
        self.saveWindowParametersToConfig()
        self._mgr.Destroy()
        wx.Frame.Destroy(self)
