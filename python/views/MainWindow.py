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

# from views.SetupWindow import SetupWindow
# from views.Question import Question
# from views.Message import Message

from services.ConfigService import ConfigService
from services.Environment import Environment

from models.Observer import Observer
#, install, options, wine_versions as wver, sp, configure, debug, gui_server
#import irc as ircgui

# Exceptions
class ErrNoProgramSelected(Exception):
   def __str__(self):
      return repr(_("You must select a program"))


class InstalledApps(wx.TreeCtrl, Observer):
    def __init__(self, frame, id):
        wx.TreeCtrl.__init__(self, frame, id, style = wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        Observer.__init__(self)
        self.frame = frame
        self.SetSpacing(0)
        self.SetIndent(5)
        self.env = Environment()
        self.config = ConfigService()
        self.iconSize = self.config.getIntSetting("ICON_SIZE", default = 32)
        
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
        for shortcut in self.getSubject().getList():
           if(searchFilter in shortcut.getName().lower()):
               self.imagesAppList.Add(shortcut.getWxIcon(self.iconSize))
               self.AppendItem(root, shortcut.getName(), i)
               i+=1
            
        # FIXME : La ca va pas, il faut creer un observateur sur le bon objet 
        if(self.env.getOS() == "Mac"):
            self.frame.playTool.Enable(False)
            self.frame.stopTool.Enable(False)
            self.frame.removeTool.Enable(False)
    
    def setIconSize(self, size = 32):
        self.iconSize = size
        self.config.setSetting("ICON_SIZE",str(size))
        self.refresh()
    
    def getIconSize(self):
        return self.iconSize
         
    def refresh(self):
        self.writeShortcuts()
        
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
        
        #wx.aui.AuiManager.Destroy(self)
        
                  
class MenuPanel(wx.Panel):
    def __init__(self, frame, id = -1):
        wx.Panel.__init__(self, frame, id)   
        self.frame = frame
        self.uiHelper = UIHelper()
        self.env = Environment()
        self.menuElem = {}
        self.menuImage = {}
        
    def addTitle(self, name, text, pos):
        self.menuElem[name] = wx.StaticText(self, -1, text, pos=(5,5+pos*20))
        self.menuElem[name].SetForegroundColour((0,0,0))
        self.menuElem[name].SetFont(self.uiHelper.getFontTitle())

    def addLink(self, name, text, pos, image, url=None):
        if(os.path.exists(image)):
            menu_icone = image
        else:
            menu_icone = self.env.getAppPath()+"/etc/playonlinux.png"

        bitmap = wx.Image(menu_icone)
        bitmap.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
        bitmap = bitmap.ConvertToBitmap()
        self.menuImage[name] = wx.StaticBitmap(self.menuPanel, id = -1, bitmap = bitmap, pos = (10,15+pos*20))

        if(url == None):
            url = ""
        
        self.menuElem[name] = wx.HyperlinkCtrl(self.menuPanel, 10000 + pos, text, url, pos=(35,15+pos*20))
        self.menuElem[name].SetNormalColour(wx.Colour(0,0,0))
        self.menuElem[name].SetVisitedColour(wx.Colour(0,0,0))
        self.menuElem[name].SetHoverColour(wx.Colour(100,100,100))

    
                
class MainWindow(wx.Frame):
    def __init__(self, id = -1):
        self.configService = ConfigService()
        self.env = Environment()
        self.uiHelper = UIHelper()
        
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
    
    

                  


        
        self.appList = InstalledApps(self, 105)
        self.menuPanel = MenuPanel(self)
   
        
        # Left menu
        self._mgr = PanelManager(self)
        self._mgr.AddPane(self.appList, wx.CENTER)
        self._mgr.AddPane(self.menuPanel, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Left().BestSize((200,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
        self._mgr.restorePosition()     
    
        self.menuPanel.Show()
             

        # Menubar
        self.drawMenuBar()
        
        # Status bar
        self.drawStatusBar()
        
        # Tool Bar
        self.drawToolBar()
        
        
        #self.writeShortcutsToWidget(True)
        
        
        
        # Program list event
        #wx.EVT_TREE_ITEM_ACTIVATED(self, 105, self.Run)
        #wx.EVT_TREE_SEL_CHANGED(self, 105, self.Select)


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

        

    def drawMenuBar(self):
        self.filemenu = wx.Menu()
        
        ### On MacOS X, preference is always on the main menu
        if(self.env.getOS() == "Mac"):
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
        
        """
        if(self.iconSize == 16):
            self.icon16.Check(True)
        if(self.iconSize == 24):
            self.icon24.Check(True)
        if(self.iconSize == 32):
            self.icon32.Check(True)
        if(self.iconSize == 48):
            self.icon48.Check(True)
"""

        # Expert menu
        self.expertmenu = wx.Menu()
        self.addMenuItem(107,  _('Manage Wine versions'), "wine.png", self.expertmenu)

        if(self.env.getOS == "Mac"):
            self.expertmenu.AppendSeparator()
            self.addMenuItem(113,  _('Read a PC cdrom'), "cdrom.png", self.expertmenu)
            

        self.expertmenu.AppendSeparator()
        self.addMenuItem(108,  _('Run a local script'), "run.png", self.expertmenu)
        self.addMenuItem(115,  _('Close all {0} software').format(self.configService.getAppName()), "wineserver.png", self.expertmenu)
        self.addMenuItem(110, _("{0} debugger").format(self.configService.getAppName()), "bug.png", self.expertmenu)
        self.addMenuItem(109, _('{0} console').format(self.configService.getAppName()), "polshell.png", self.expertmenu)
       
        self.expertmenu.AppendSeparator()
        self.addMenuItem(112, self.configService.getAppName()+" online", "playonlinux_online.png", self.expertmenu)
        self.addMenuItem(111, _("{0} messenger").format(self.configService.getAppName()), "people.png", self.expertmenu)
        
        # Option menu
        self.optionmenu = wx.Menu()
        
        self.addMenuItem(221, _("Internet"), "internet.png", self.optionmenu)
        self.addMenuItem(212,  _("File associations"), "extensions.png", self.optionmenu)
        self.addMenuItem(213,  _("Plugin manager"), "plugins.png", self.optionmenu)

        self.help_menu = wx.Menu()
        self.addMenuItem(wx.ID_ABOUT,  _('About {0}').format(self.configService.getAppName()), None, self.help_menu)

        self.pluginsmenu = wx.Menu()

        plugin_files = os.listdir(self.env.getAppPath()+"/plugins")
        plugin_files.sort()
        self.plugin_list = []
        
        for plugin in plugin_files:
            if(os.path.exists(self.env.getUserRoot()+"/plugins/"+plugin+"/scripts/menu")):
                if(os.path.exists(self.env.getUserRoot()+"/plugins/"+plugin+"/enabled")):

                    plugin_icon = self.env.getUserRoot()+"/plugins/"+plugin+"/icon"
                    
                    if(not os.path.exists(plugin_icon)):
                        plugin_icon = self.configService.getAppPath()+"/resources/icons/playonlinux16.png"

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
        wx.EVT_MENU(self, 501,  self.changeIconSize)
        wx.EVT_MENU(self, 502,  self.changeIconSize)
        wx.EVT_MENU(self, 503,  self.changeIconSize)
        wx.EVT_MENU(self, 504,  self.changeIconSize)

        # Expert
        wx.EVT_MENU(self, 107,  self.WineVersion)
        wx.EVT_MENU(self, 108,  self.scriptRunLocalScript)
        wx.EVT_MENU(self, 109,  self.PolShell)
        wx.EVT_MENU(self, 110,  self.BugReport)
        wx.EVT_MENU(self, 111,  self.OpenIrc)
        wx.EVT_MENU(self, 112,  self.POLOnline)
        wx.EVT_MENU(self, 113,  self.PCCd)
        wx.EVT_MENU(self, 115,  self.scriptKillall)
        wx.EVT_MENU(self, 121,  self.Configure)
        wx.EVT_MENU(self, 122,  self.Package)
        wx.EVT_TEXT(self, 124,  self.searchEvent)

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
        self.playTool = self.toolbar.AddLabelTool(wx.ID_OPEN, _("Run"), self.uiHelper.getBitmap("toolbar/play.png"))
        self.stopTool = self.toolbar.AddLabelTool(123, _("Close"), self.uiHelper.getBitmap("toolbar/stop.png"))

        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_ADD, _("Install"), self.uiHelper.getBitmap("toolbar/install.png"))
        self.removeTool = self.toolbar_remove = self.toolbar.AddLabelTool(wx.ID_DELETE, _("Remove"), self.uiHelper.getBitmap("toolbar/delete.png"))
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(121, _("Configure"), self.uiHelper.getBitmap("toolbar/configure.png"))

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
        
        wx.EVT_MENU(self,  wx.ID_DELETE,  self.UninstallGame)

        
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
            playOnLinuxApppolDie()
            GuiServer().getState().release(scriptPid)
        
        if(command == "POL_Restart"):
            playOnLinuxApp.polRestart()
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
           
        
        
        # Other 
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
                print "Err. Please use POL_SetupWindow_Init first"
                GuiServer().getState().release(scriptPid)  
            else: 
                try:
                    setupWindowFunction = getattr(setupWindowObject, command)
                except AttributeError:
                    Error ('Function not found "%s" (%s)' % (command, arguments) )
                else:
                    try:
                        setupWindowFunction(*arguments)
                    except TypeError, e:
                        print 'Error: %s (%s)' % (e, arguments)
        
           
           
    def TimerAction(self, event):
        #self.StatusRead()
        self.writeShortcutsToWidget()
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
        

    def addMenuItem(self, id, title, icon, menu):
        if(icon != None):
            item = wx.MenuItem(menu, id, title)            
            item.SetBitmap(self.uiHelper.getBitmap("menu/"+icon))
            menu.AppendItem(item)
        else:
            menu.Append(id, title)
            
        
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

    def Select(self, event):
        game_exec = self.getSelectedShortcut().getName()
        
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



            if(os.path.exists(icon)):
                try:
                    self.bitmap = wx.Image(icon)
                    if(self.bitmap.GetWidth() >= 48):
                        self.bitmap.Rescale(48,48,wx.IMAGE_QUALITY_HIGH)
                        self.bitmap = self.bitmap.ConvertToBitmap()
                        self.menuBitmap = wx.StaticBitmap(self.menuPanel, id=-1, bitmap=self.bitmap, pos=(left_pos,20+(i+2)*20))
                except:
                    pass

    def donate(self, event):
        if(Context().getOS() == "Mac"):
            webbrowser.open("http://www.playonmac.com/en/donate.html")
        else:
            webbrowser.open("http://www.playonlinux.com/en/donate.html")


    def searchEvent(self, event):
        self.writeShortcutsToWidget(forceRefresh = True, searchFilter = self.searchbox.GetValue().encode("utf-8","replace").lower())


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

    def PolShell(self, event):
        self.polshell = PrivateGUIScript("POLShell")
        self.polshell.start()
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

    
        
    def Run(self, event, s_debug=False):
        self.selectedProgram =  self.getSelectedShortcut()
        selectedProgram = self.selectedProgram
        game_exec = selectedProgram.getName()
        game_prefix = selectedProgram.getPrefix()

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
  
                selectedProgram.run()
            else:
                wx.MessageBox(_("Please select a program."), Context().getAppName())
        else:
            wx.MessageBox(_("The virtual drive associated with {0} ({1}) does no longer exists.").format(game_exec, game_prefix.getName()), Context().getAppName())

    def RunDebug(self, event):
        game_exec = self.getSelectedShortcut()
        playonlinux.SetDebugState(game_exec, True)
        self.Run(self, True)



    # Getters
    def getAppList(self):
        return self.appList
           
           
    def aboutPlayOnLinux(self):
        # FIXME
        aboutWindow = PolAbout()
        aboutWindow.show()   
        
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
