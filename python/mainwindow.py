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

import os, getopt, sys, urllib, signal, string, time, webbrowser, gettext, locale, sys, shutil, subprocess
#locale.setlocale(locale.CODESET,'fr_FR.utf8')

#try:
#	locale.getlocale()
#except:
#	os.environ["LANG"] = "en_US.utf-8"
#locale.setlocale(locale.LC_ALL, '.utf-8')

if(os.environ["POL_OS"] == "Linux"):
	import wxversion
	wxversion.ensureMinimal('2.8')
	
import wx
import wx.aui

import lib.Variables as Variables, lib.lng as lng
import lib.playonlinux as playonlinux
import guiv3 as gui, install, options, wine_versions as wver, sp, configure, threading, debug
import irc as ircgui

class POLWeb(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.sendToStatusBarStr = ""
		self.sendAlertStr = None
		self.Gauge = False
		self.WebVersion = ""
		self.Show = False
		self.perc = -1
		
	def sendToStatusBar(self, message, gauge):
		self.sendToStatusBarStr = message
		self.Gauge = gauge
		self.Show = True

	def sendPercentage(self, n):
		self.perc = n

	def sendAlert(self, message):
		self.sendAlertStr = message
			
	def LastVersion(self):
		if(os.environ["POL_OS"] == "Mac"):
			fichier_online="version_mac"
		else:
			fichier_online="version2"
		return os.popen(os.environ["POL_WGET"]+' "'+os.environ["SITE"]+'/'+fichier_online+'.php?v='+os.environ["VERSION"]+'" -T 30 -O-','r').read()
	
	def real_check(self):
		self.WebVersion = self.LastVersion()
		
		if(self.WebVersion == ""):
			self.sendToStatusBar(_('{0} website is unavailable. Please check your connexion').format(os.environ["APPLICATION_TITLE"]), False)
		else:
			self.sendToStatusBar(_("Refreshing {0}").format(os.environ["APPLICATION_TITLE"]), True)
			exe = ['bash',Variables.playonlinux_env+"/bash/pol_update_list"]
			
			p = subprocess.Popen(exe, stdout=subprocess.PIPE)
			
			while(True):
				retcode = p.poll() #returns None while subprocess is running
				line = p.stdout.readline()
				try:
					self.sendPercentage(int(line))
				except:
					pass
				#yield line
				if(retcode is not None):
					break
			
			if(playonlinux.VersionLower(os.environ["VERSION"],self.WebVersion)):
				self.sendToStatusBar(_('An updated version of {0} is available').format(os.environ["APPLICATION_TITLE"])+" ("+self.WebVersion+")",False)
				if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
					self.sendAlert(_('An updated version of {0} is available').format(os.environ["APPLICATION_TITLE"])+" ("+self.WebVersion+")")
				os.environ["POL_UPTODATE"] = "FALSE"
			else:
				self.Show = False
				self.perc = -1
				os.environ["POL_UPTODATE"] = "TRUE"
		
		self.wantcheck = False
			
	def check(self):
		self.wantcheck = True	
			
	def run(self):
		self.check()
		while(1):
			if(self.wantcheck == True):
				self.real_check()
			time.sleep(1)
		

		    
class MainWindow(wx.Frame):
  def __init__(self,parent,id,title):
			
	wx.Frame.__init__(self, parent, 1000, title, size = (515,450))
	self.SetMinSize((400,400))
	
	self.menuElem = {}
	self.menuImage = {}
	
	# Window size
	try:
		self.windowWidth = int(playonlinux.GetSettings("MAINWINDOW_WIDTH"))
		self.windowHeight = int(playonlinux.GetSettings("MAINWINDOW_HEIGHT"))
		self.SetSize((self.windowWidth,self.windowHeight))
	except:
		self.windowWidth = 450
		self.windowHeight = 450
		
	try:
		self.windowx = int(playonlinux.GetSettings("MAINWINDOW_X"))
		self.windowy = int(playonlinux.GetSettings("MAINWINDOW_Y"))
		self.screen_width = wx.Display().GetGeometry()[2]
		self.screen_height = wx.Display().GetGeometry()[3]
		
		if(self.screen_width >= self.windowx and self.screen_height >= self.windowy):
			self.SetPosition((self.windowx, self.windowy))
		else:
			self.Center(wx.BOTH)
	except:
		self.Center(wx.BOTH)
				
	self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
	self.timer = wx.Timer(self, 1)
	
	try:
		self.iconSize = int(playonlinux.GetSettings("ICON_SIZE"))
	except:
		self.iconSize = 32
	
		
	self.images = wx.ImageList(self.iconSize, self.iconSize)
	self.imagesEmpty = wx.ImageList(1,1)
	
	self.updater = POLWeb()
	self.updater.start()
	self.sendAlertStr = None
	
	## Fonts
	if(os.environ["POL_OS"] == "Mac"):
		self.fontTitre = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
		self.fontText = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
	else :
		self.fontTitre = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
		self.fontText = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
	
	
	## List game
	self.list_game = wx.TreeCtrl(self, 105, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)	
	self.list_game.SetSpacing(0);
	self.list_game.SetIndent(5);
	self.list_game.SetImageList(self.images)
	
	self._mgr = wx.aui.AuiManager(self)
	self.menu_gauche = wx.Panel(self,-1)
	

	
	self._mgr.AddPane(self.list_game, wx.CENTER)		
	self.oldreload = ""	
	self.oldimg = ""
	
	self.filemenu = wx.Menu()
	if(os.environ["POL_OS"] == "Mac"):
		prefItem = self.filemenu.Append(wx.ID_PREFERENCES, text = "&Preferences")
		self.Bind(wx.EVT_MENU, self.Options, prefItem)
	
	### TOOLBAR
	self.filemenu.Append(wx.ID_OPEN, _("Run"))
	self.filemenu.Append(wx.ID_ADD, _("Install"))
	self.filemenu.Append(wx.ID_DELETE, _("Remove"))
	self.filemenu.AppendSeparator()
	self.filemenu.Append(216, _("Donate"))
	self.filemenu.Append(wx.ID_EXIT, _("Exit"))
	
	### MENU
	self.displaymenu = wx.Menu()
	self.icon16 = self.displaymenu.AppendRadioItem(501, _("Small icons"))
	self.icon24 = self.displaymenu.AppendRadioItem(502, _("Medium icons"))
	self.icon32 = self.displaymenu.AppendRadioItem(503, _("Large icons"))
	self.icon48 = self.displaymenu.AppendRadioItem(504, _("Very large icons"))
	#self.displaymenu.AppendSeparator()
	#self.panDisplay = self.displaymenu.AppendCheckItem(505, _("Show panel"))
	
	if(self.iconSize == 16):
		self.icon16.Check(True)
	if(self.iconSize == 24):
		self.icon24.Check(True)
	if(self.iconSize == 32):
		self.icon32.Check(True)
	if(self.iconSize == 48):
		self.icon48.Check(True)
		
	self.expertmenu = wx.Menu()

	self.winever_item = wx.MenuItem(self.expertmenu, 107, _("Manage Wine versions"))
	self.winever_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/wine.png"))
	self.expertmenu.AppendItem(self.winever_item)

	if(os.environ["POL_OS"] == "Mac"):
		self.expertmenu.AppendSeparator()
		self.pccd_item = wx.MenuItem(self.expertmenu, 113, _("Read a PC CD-Rom"))
		self.pccd_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/cdrom.png"))
		self.expertmenu.AppendItem(self.pccd_item)
		
	self.expertmenu.AppendSeparator()

	self.run_item = wx.MenuItem(self.expertmenu, 108, _("Run a local script"))
	self.run_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/run.png"))
	self.expertmenu.AppendItem(self.run_item)
		
	self.wineserv_item = wx.MenuItem(self.expertmenu, 115, _('Close all {0} software').format(os.environ["APPLICATION_TITLE"]))
	self.wineserv_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/wineserver.png"))
	self.expertmenu.AppendItem(self.wineserv_item)

	self.polshell_item = wx.MenuItem(self.expertmenu, 109, _('{0} console').format(os.environ["APPLICATION_TITLE"]))
	self.polshell_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/polshell.png"))
	self.expertmenu.AppendItem(self.polshell_item)

	self.expertmenu.AppendSeparator()

	self.pol_online = wx.MenuItem(self.expertmenu, 112, os.environ["APPLICATION_TITLE"]+" online")
	self.pol_online.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/playonlinux_online.png"))
	self.expertmenu.AppendItem(self.pol_online)

	self.chat_item = wx.MenuItem(self.expertmenu, 111, _("{0} messenger").format(os.environ["APPLICATION_TITLE"]))
	self.chat_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/people.png"))
	self.expertmenu.AppendItem(self.chat_item)
		
	self.bug_item = wx.MenuItem(self.expertmenu, 110, _("{0} debugger").format(os.environ["APPLICATION_TITLE"]))
	self.bug_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/bug.png"))
	self.expertmenu.AppendItem(self.bug_item)
	
	
	self.optionmenu = wx.Menu()


	self.option_item = wx.MenuItem(self.expertmenu, 211, _("Internet"))
	self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/internet-web-browser.png"))
	self.optionmenu.AppendItem(self.option_item)

	self.option_item = wx.MenuItem(self.expertmenu, 212, _("File associations"))
	self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/extensions.png"))
	self.optionmenu.AppendItem(self.option_item)


	
	self.help_menu = wx.Menu()
	self.help_menu.Append(wx.ID_ABOUT, _('About {0}').format(os.environ["APPLICATION_TITLE"]))

	self.pluginsmenu = wx.Menu()

	files=os.listdir(Variables.playonlinux_rep+"/plugins")
	files.sort()
	self.plugin_list = []
	self.i = 0
	self.j = 0
	while(self.i < len(files)):
		if(os.path.exists(Variables.playonlinux_rep+"/plugins/"+files[self.i]+"/scripts/menu")):
			if(os.path.exists(Variables.playonlinux_rep+"/plugins/"+files[self.i]+"/enabled")):
				self.plugin_item = wx.MenuItem(self.expertmenu, 300+self.j, files[self.i])
				
				self.icon_look_for = Variables.playonlinux_rep+"/plugins/"+files[self.i]+"/icon"
				if(os.path.exists(self.icon_look_for)):
					self.bitmap = wx.Bitmap(self.icon_look_for)
				else:
					self.bitmap = wx.Bitmap(Variables.playonlinux_env+"/etc/playonlinux16.png")

				self.plugin_item.SetBitmap(self.bitmap)
				self.pluginsmenu.AppendItem(self.plugin_item)
				wx.EVT_MENU(self, 300+self.j,  self.run_plugin)
				self.plugin_list.append(files[self.i])
				self.j += 1
		self.i += 1

	if(self.j > 0):
		self.pluginsmenu.AppendSeparator()

	self.option_item_p = wx.MenuItem(self.expertmenu, 214, _("Plugin manager"))
	self.option_item_p.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/package-x-generic.png"))
	self.pluginsmenu.AppendItem(self.option_item_p)
	
	self.option_item = wx.MenuItem(self.expertmenu, 214, _("Plugin manager"))
	self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/package-x-generic.png"))
	self.optionmenu.AppendItem(self.option_item)

	
	self.last_string = ""

	self.sb = wx.StatusBar(self, -1 )
	self.sb.SetFieldsCount(2)
	self.sb.SetStatusWidths([400, -1])
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
	self.playTool = self.toolbar.AddLabelTool(wx.ID_OPEN, _("Run"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/play.png"))
	self.stopTool = self.toolbar.AddLabelTool(123, _("Close"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/stop.png"))
	
	self.toolbar.AddSeparator()
	self.toolbar.AddLabelTool(wx.ID_ADD, _("Install"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/install.png"))
	self.removeTool = self.toolbar_remove = self.toolbar.AddLabelTool(wx.ID_DELETE, _("Remove"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/delete.png"))
	#self.toolbar.AddLabelTool(120, _("CD-ROM"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/cdrom.png"))
	
	self.toolbar.AddSeparator()
	self.toolbar.AddLabelTool(121, _("Configure"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/configure.png"))
	#self.toolbar.AddLabelTool(122, _("Shortcut"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/package.png"))
	#self.toolbar.AddLabelTool(123, _("Messenger"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/messenger.png"))

	#self.toolbar.DoMenuUpdate(self.toolbar)
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
	#wx.EVT_TREE_ITEM_MENU(self, 105, self.OnRightDown)

	#Timer, regarde toute les secondes si il faut actualiser la liste
	
	self.Bind(wx.EVT_TIMER, self.AutoReload, self.timer)
	self.timer.Start(1000)

	#Pop-up menu for game list: beginning
	wx.EVT_TREE_ITEM_MENU(self, 105, self.RMBInGameList)
	wx.EVT_MENU(self, 230, self.RWineConfigurator)
	wx.EVT_MENU(self, 231, self.RRegistryEditor)
	wx.EVT_MENU(self, 232, self.GoToAppDir)
	wx.EVT_MENU(self, 233, self.ChangeIcon)
	wx.EVT_MENU(self, 234, self.UninstallGame)
	wx.EVT_MENU(self, 235, self.RKill)
	wx.EVT_MENU(self, 236, self.ReadMe)
	self.MgrAddPage()
	
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

	#try:
	#self._mgr.ClosePane(wx.aui.AuiPaneInfo().Name('Actions'))
	#except:
	#	pass
	#if(self.LoadPosition != "NONE"):
	if(self.LoadPosition == "LEFT"):
		self._mgr.AddPane(self.menu_gauche, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Left().BestSize((self.LoadSize,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
	else:
		self._mgr.AddPane(self.menu_gauche, wx.aui.AuiPaneInfo().Name('Actions').Caption('Actions').Right().BestSize((self.LoadSize,400)).Floatable(True).CloseButton(False).TopDockable(False).BottomDockable(False))
	self.menu_gauche.Show()
	#else:
	#	self.menu_gauche.Hide()
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

	if(self.updater.Show == True):
		self.sb.Show()
		try:
			self.installFrame.panelItems.Hide()
			self.installFrame.panelManual.Hide()
			self.installFrame.panelWait.Show()
			self.installFrame.animation_wait.Play()
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
			self.installFrame.Refresh()
		except:
			pass
	if(self.updater.sendAlertStr != self.sendAlertStr):
		wx.MessageBox(self.updater.sendAlertStr, os.environ["APPLICATION_TITLE"])
		self.sendAlertStr = self.updater.sendAlertStr
		
  def RMBInGameList(self, event):
	self.GameListPopUpMenu = wx.Menu()

	self.ConfigureWine = wx.MenuItem(self.GameListPopUpMenu, 230, _("Configure Wine"))
	self.ConfigureWine.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/run.png"))
	self.GameListPopUpMenu.AppendItem(self.ConfigureWine)

	self.RegistryEditor = wx.MenuItem(self.GameListPopUpMenu, 231, _("Registry Editor"))
	self.RegistryEditor.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/regedit.png"))
	self.GameListPopUpMenu.AppendItem(self.RegistryEditor)

	self.GotoAppDir = wx.MenuItem(self.GameListPopUpMenu, 232, _("Open the application's directory"))
	self.GotoAppDir.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/folder-wine.png"))
	self.GameListPopUpMenu.AppendItem(self.GotoAppDir)

	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 236, _("Read the manual"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/manual.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)
	
	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 233, _("Set the icon"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/change_icon.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 234, _("Remove"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/delete.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 235, _("Close this application"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/media-playback-stop.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

	self.PopupMenu(self.GameListPopUpMenu, event.GetPoint())
    #if(len(sys.argv) >= 1):

    #wx.MessageBox(str(sys.argv), "PlayOnLinux", wx.OK)


  def RWineConfigurator(self, event):
        self.RConfigure(_("Configure Wine"), "nothing")

  def RKill(self, event):
        self.RConfigure(_("KillApp"), "nothing")

  def ReadMe(self, event):
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
	if(os.path.exists(os.environ["POL_USER_ROOT"]+"/configurations/manuals/"+game_exec)):
		playonlinux.POL_Open(os.environ["POL_USER_ROOT"]+"/configurations/manuals/"+game_exec)
	else:
		wx.MessageBox(_("No manual found for {0}").format(game_exec), os.environ["APPLICATION_TITLE"])
	
  def RRegistryEditor(self, event):
        self.RConfigure(_("Registry Editor"), "nothing")

  def run_plugin(self, event):
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
	plugin=self.plugin_list[event.GetId()-300]
	try :
		os.system("bash \""+Variables.playonlinux_rep+"/plugins/"+plugin+"/scripts/menu\" \""+game_exec+"\"&")
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
		
  def GoToAppDir(self, event):
		self.game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
		playonlinux.open_folder(self.game_exec)
		
  def ChangeIcon(self, event):
		self.IconDir = Variables.homedir+"/.local/share/icons/"
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
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
	self.read = open(Variables.playonlinux_rep+"shortcuts/"+game_exec,"r").readlines()
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
	self.menuGaucheAddTitle("pol_title", os.environ["APPLICATION_TITLE"], i)
	i+=1
	self.menuGaucheAddLink("pol_prgm_install", _("Install a program"), i,Variables.playonlinux_env+"/resources/images/menu/add.png",self.InstallMenu)
	i+=1
	self.menuGaucheAddLink("pol_prgm_settings", _("Settings"), i,Variables.playonlinux_env+"/resources/images/menu/settings.png",self.Options)
	i+=1
	self.menuGaucheAddLink("pol_prgm_messenger", _("Messenger"), i,Variables.playonlinux_env+"/resources/images/menu/people.png",self.OpenIrc)

	
	if(shortcut != None):
		i+=2
		self.menuGaucheAddTitle("prgm_title", shortcut, i)
		i+=1
		self.menuGaucheAddLink("pol_prgm_run", _("Run"), i,Variables.playonlinux_env+"/resources/images/menu/media-playback-start.png",self.Run)
		i+=1
		self.menuGaucheAddLink("pol_prgm_kill", _("Close"), i,Variables.playonlinux_env+"/resources/images/menu/media-playback-stop.png",self.RKill)
		i+=1
		self.menuGaucheAddLink("pol_prgm_rundebug", _("Debug"), i,Variables.playonlinux_env+"/resources/images/menu/bug.png",self.RunDebug)
		i+=1
		self.menuGaucheAddLink("pol_prgm_configure", _("Configure"), i,Variables.playonlinux_env+"/resources/images/menu/run.png",self.Configure)
		i+=1
		self.menuGaucheAddLink("pol_prgm_shortcut", _("Create a shortcut"), i,Variables.playonlinux_env+"/resources/images/menu/shortcut.png",self.Package)
		i+=1
		self.menuGaucheAddLink("pol_prgm_adddir", _("Open the directory"), i,Variables.playonlinux_env+"/resources/images/menu/folder-wine.png",self.GoToAppDir)
		
		if(os.path.exists(os.environ["POL_USER_ROOT"]+"/configurations/manuals/"+shortcut)):
			i+=1
			self.menuGaucheAddLink("pol_prgm_readme", _("Read the manual"), i,Variables.playonlinux_env+"/resources/images/menu/manual.png",self.ReadMe)
		
		i+=1
		self.menuGaucheAddLink("pol_prgm_uninstall", _("Uninstall"), i,Variables.playonlinux_env+"/resources/images/menu/window-close.png",self.UninstallGame)
				
		
		self.linksfile = os.environ["POL_USER_ROOT"]+"/configurations/links/"+shortcut
		if(os.path.exists(self.linksfile)):
			self.linksc = open(self.linksfile,"r").read().split("\n")
			for line in self.linksc:
				if("|" in line):
					line = line.split("|")
					i+=1
					if("PROFILEBUTTON/" in line[0]):
						line[0] = line[0].replace("PROFILEBUTTON/","")
						
					self.menuGaucheAddLink("url_"+str(i), line[0], i,Variables.playonlinux_env+"/resources/images/menu/star.png",None,line[1])
								
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
	self.menuElem[id].SetFont(self.fontTitre)

	
  def menuGaucheAddLink(self,id,text,pos,image,evt,url=None):
	if(os.path.exists(image)):
		menu_icone = image
	else:
		menu_icone = Variables.playonlinux_env+"/etc/playonlinux.png"
		
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
	self.games = os.listdir(Variables.playonlinux_rep+"shortcuts/")
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
		if(not os.path.isdir(Variables.playonlinux_rep+"/shortcuts/"+game)):
			if(os.path.exists(Variables.playonlinux_rep+"/icones/"+self.iconFolder+"/"+game)):
				file_icone = Variables.playonlinux_rep+"/icones/"+self.iconFolder+"/"+game
			else:
				file_icone = Variables.playonlinux_env+"/etc/playonlinux.png"

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
		game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
		if(game_exec != ""):
			os.system("bash \""+Variables.playonlinux_env+"/bash/polconfigurator\" \""+game_exec+"\" \""+function_to_run+"\" \""+firstargument+"\"&")
		else:
			wx.MessageBox(_("Please select a program."), os.environ["APPLICATION_TITLE"])
	    
	
  def Options(self, event):
    onglet=event.GetId()
    try:
		self.optionFrame.SetFocus()
    except:
		self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(os.environ["APPLICATION_TITLE"]), 2)
		if(onglet == 211):
			self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(os.environ["APPLICATION_TITLE"]), 0)
		if(onglet == 214):
			self.optionFrame = options.MainWindow(self, -1, _("{0} settings").format(os.environ["APPLICATION_TITLE"]), 1)
		self.optionFrame.Center(wx.BOTH)
		self.optionFrame.Show(True)

  def killall(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/killall\"&")

  def Executer(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/expert/Executer\"&")

  def BugReport(self, event):
	try:
		self.debugFrame.Show()
		self.debugFrame.SetFocus()
	except:
		self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(os.environ["APPLICATION_TITLE"]))
		self.debugFrame.Center(wx.BOTH)
		self.debugFrame.Show()
		

  def POLOnline(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/playonlinux_online\" &")

  def PCCd(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/read_pc_cd\" &")

  def PolShell(self, event):
    #Variables.run_x_server()
    os.system("bash \""+Variables.playonlinux_env+"/bash/expert/PolShell\"&")

  def Configure(self, event):
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
	try:
		self.configureFrame.Show(True)
		self.configureFrame.SetFocus()
		if(game_exec != ""):
			self.configureFrame.change_program(game_exec,False)
			
	except:
		if(game_exec == ""):
			self.configureFrame = configure.MainWindow(self, -1, _("{0} configuration").format(os.environ["APPLICATION_TITLE"]),"default",True)
		else:
			self.configureFrame = configure.MainWindow(self, -1, _("{0} configuration").format(os.environ["APPLICATION_TITLE"]),game_exec.decode("utf-8","replace"),False)
	
		
		self.configureFrame.Center(wx.BOTH)
		self.configureFrame.Show(True)

    #os.system("bash \""+Variables.playonlinux_env+"/bash/polconfigurator\" \""+game_exec+"\"&")

  def Package(self, event):
    game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
    os.system("bash \""+Variables.playonlinux_env+"/bash/make_shortcut\" \""+game_exec.encode("utf-8","replace")+"\"&")

  def UninstallGame(self, event):
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
	if(game_exec != ""):
		os.system("bash \""+Variables.playonlinux_env+"/bash/uninstall\" \""+game_exec.encode("utf-8","replace")+"\"&")
	else:
		wx.MessageBox(_("Please select a program."), os.environ["APPLICATION_TITLE"])

  def AutoReload(self, event):
	
	self.StatusRead()
	fichier_index = os.environ["REPERTOIRE"]+"/configurations/guis/index_"+os.environ["POL_ID"]
	#print(fichier_index)
	try:
		message = open(fichier_index,'r').read()
	except:
		open(fichier_index,'a').write('')
		message = open(fichier_index,'r').read()
	message = string.split(message, "\n")
	if(message[0] == "Open"):
		self.frame = gui.POL_SetupFrame(os.environ["APPLICATION_TITLE"],message[1].replace("\n",""),message[2].replace("\n",""),message[3].replace("\n",""),message[4].replace("\n",""),message[5].replace("\n",""))
		self.frame.Center(wx.BOTH)
		self.frame.Show(True)
		open(fichier_index,'w').write("Wait")

	reload = os.listdir(Variables.playonlinux_rep+"/shortcuts")
	if(reload != self.oldreload):
		self.Reload(self)
		self.oldreload = reload

	reloadimg = os.listdir(Variables.playonlinux_rep+"/icones/32")
	if(reloadimg != self.oldimg):
		self.Reload(self)
		self.oldimg = reloadimg

  def InstallMenu(self, event):
    try:
    	self.installFrame.Show(True)
    	self.installFrame.SetFocus()
    except:
    	self.installFrame = install.InstallWindow(self, -1, _('{0} install menu').format(os.environ["APPLICATION_TITLE"]))
    	self.installFrame.Center(wx.BOTH)
    	self.installFrame.Show(True)
	
  def WineVersion(self, event):
    try:
    	self.wversion.Show()
    	self.wversion.SetFocus()
    except:
    	self.wversion = wver.MainWindow(None, -1, _('{0} wine versions manager').format(os.environ["APPLICATION_TITLE"]))
    	self.wversion.Center(wx.BOTH)
    	self.wversion.Show(True)
	#os.system("bash \""+Variables.playonlinux_env+"/bash/wineversion\"&")

  def Run(self, event, s_debug=False):
	
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
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
					self.debugFrame = debug.MainWindow(None, -1, _("{0} debugger").format(os.environ["APPLICATION_TITLE"]),game_prefix,0)
					self.debugFrame.Center(wx.BOTH)
					self.debugFrame.Show()
			
			os.system("bash "+Variables.playonlinux_env+"/bash/run_app \""+game_exec+"\"&")
		else:
			wx.MessageBox(_("Please select a program."), os.environ["APPLICATION_TITLE"])
	else:
		wx.MessageBox(_("The virtual drive associated with {0} ({1}) does no longer exists.").format(game_exec, game_prefix), os.environ["APPLICATION_TITLE"])
 
  def RunDebug(self, event):
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8","replace")
	game_prefix = playonlinux.getPrefix(game_exec)
	playonlinux.SetDebugState(game_exec, True)
	self.Run(self, True)
		
  def ClosePol(self, event):
    if(wx.YES == wx.MessageBox(_('Are you sure you want to close all {0} Windows?').format(os.environ["APPLICATION_TITLE"]).decode("utf-8","replace"),os.environ["APPLICATION_TITLE"], style=wx.YES_NO | wx.ICON_QUESTION)):
		os.remove(Variables.playonlinux_rep+"/configurations/guis/index_"+os.environ["POL_ID"])
		self.SizeToSave = self.GetSize();
		self.PositionToSave = self.GetPosition();
		# Save size and position
		playonlinux.SetSettings("MAINWINDOW_WIDTH",str(self.SizeToSave[0]))
		playonlinux.SetSettings("MAINWINDOW_HEIGHT",str(self.SizeToSave[1]-Variables.windows_add_playonmac*56))
		playonlinux.SetSettings("MAINWINDOW_X",str(self.PositionToSave[0]))
		playonlinux.SetSettings("MAINWINDOW_Y",str(self.PositionToSave[1]))
		self._mgr.UnInit()
		# I know, that's very ugly, but I have no choice for the moment
		self.perspective = self._mgr.SavePerspective().split("|")
		self.perspective = self.perspective[len(self.perspective) - 2].split("=")
		
		self.DockType = self.perspective[0]
		self.mySize = 200
		self.myPosition = "LEFT"
		
		#if(self.DockType == "dock_size(5,0,0)"):
		#	self.myPosition = "NONE"
		#print self.DockType
		
		if(self.DockType == "dock_size(4,0,0)"):
			self.mySize = int(self.perspective[1]) - 2
			self.myPosition = "LEFT"

		if(self.DockType == "dock_size(2,0,1)" or self.DockType == "dock_size(2,0,0)" or "dock_size(2," in self.DockType):
			self.mySize = int(self.perspective[1]) - 2
			self.myPosition = "RIGHT"

		playonlinux.SetSettings("PANEL_SIZE",str(self.mySize))
		playonlinux.SetSettings("PANEL_POSITION",str(self.myPosition))
		
		os._exit(0)
    return None
    
  def About(self, event):
    self.aboutBox = wx.AboutDialogInfo()
    if(os.environ["POL_OS"] == "Linux"):
    	self.aboutBox.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))


    self.aboutBox.SetName(os.environ["APPLICATION_TITLE"])
    self.aboutBox.SetVersion(Variables.version)
    self.aboutBox.SetDescription(_("Run your Windows programs on "+os.environ["POL_OS"]+" !"))
    self.aboutBox.SetCopyright(_("(C) PlayOnLinux and PlayOnMac team 2012\nUnder GPL licence version 3"))
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
		lng.iLang()
		close = False
		exe_present = False
		
		self.systemCheck()
				
		for f in  sys.argv[1:]:		
			self.MacOpenFile(f)
			if(".exe" in f or ".EXE" in f):
				exe_present = True
			close = True
			
		if(close == True and exe_present == False):
			os._exit(0)
			
		self.SetClassName(os.environ["APPLICATION_TITLE"])
		self.SetAppName(os.environ["APPLICATION_TITLE"])
		#self.icon = wx.TaskBarIcon()
		#self.icon.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonmac.png", wx.BITMAP_TYPE_ANY))
		self.frame = MainWindow(None, -1, os.environ["APPLICATION_TITLE"])
		self.SetTopWindow(self.frame)
		#self.frame.Center(wx.BOTH)
		self.frame.Show(True)
		
		return True
	
	def singleCheck(self, package, fatal=True):
		devnull = open('/dev/null', 'wb')
		try:
			returncode=subprocess.call(["which",package],stdout=devnull)
		except:
			returncode=255
		
		if(fatal == True):
			message = "You need to install it to continue"
		else:
			message = "You should install it to use {0}"
			
		if(returncode != 0):
			wx.MessageBox(_("{0} cannot find {1}.\n\n"+message).format(os.environ["APPLICATION_TITLE"],package),_("Error"))
			if(fatal == True):
				os._exit(1)
			
	def systemCheck(self):
		#### Root uid check
		if(os.popen("id -u").read() == "0\n" or os.popen("id -u").read() == "0"):
			wx.MessageBox(_("{0} is not supposed to be run as root. Sorry").format(os.environ["APPLICATION_TITLE"]),_("Error"))
			os._exit(1)			
		
		#### 32 bits OpenGL check
		try:
			returncode=subprocess.call([os.environ["PLAYONLINUX"]+"/bash/check_gl","x86"])
		except:
			returncode=255
		if(os.environ["POL_OS"] == "Linux" and returncode != 0):
			wx.MessageBox(_("{0} is unable to find 32bits OpenGL libraries.\n\nYou might encounter problem with your games").format(os.environ["APPLICATION_TITLE"]),_("Error"))
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
			wx.MessageBox(_("{0} is unable to find 64bits OpenGL libraries.\n\nYou might encounter problem with your games").format(os.environ["APPLICATION_TITLE"]),_("Error"))
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
				wx.MessageBox(_("Your filesystem might prevent {0} from running correctly.\n\nPlease open {0} in a terminal to get more details").format(os.environ["APPLICATION_TITLE"]),_("Error"))
		
		#### Optirun check
		"""
		try:
			returncode=subprocess.call(["which","optirun"])
		except:
			returncode=255
		
		if(returncode == 0):
			if(playonlinux.GetSettings("OPTIRUN_ASKED") == ""):
				playonlinux.SetSettings("OPTIRUN_ASKED","TRUE")
				if(wx.YES == wx.MessageBox(_('{0} has detected that optirun is installed on your system.\n\nDo you want {0} to be configured to use it?').format(os.environ["APPLICATION_TITLE"]).decode("utf-8","replace"), os.environ["APPLICATION_TITLE"],style=wx.YES_NO | wx.ICON_QUESTION)):
					playonlinux.SetSettings("PRE_WINE","optirun")
		"""
		
		if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
			if(playonlinux.GetSettings("SEND_REPORT") == ""):
				if(wx.YES == wx.MessageBox(_('Do you want to help {0} to make a compatibility database?\n\nIf you click yes, the following things will be sent to us anonymously the first time you run a Windows program:\n\n- You graphic card model\n- Your OS version\n- If graphic drivers are installed or not.\n\n\nThese information will be very precious for us to help people.').format(os.environ["APPLICATION_TITLE"]).decode("utf-8","replace"), os.environ["APPLICATION_TITLE"],style=wx.YES_NO | wx.ICON_QUESTION)):
					playonlinux.SetSettings("SEND_REPORT","TRUE")
				else:
					playonlinux.SetSettings("SEND_REPORT","TRUE")
							
		#### Other import checks
		self.singleCheck("tar")
		self.singleCheck("cabextract")
		self.singleCheck("convert")
		self.singleCheck("wget")
		self.singleCheck("gpg")
		if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
			self.singleCheck("xterm",False)
		self.singleCheck("gettext.sh",False)
		self.singleCheck("icotool",False)
		self.singleCheck("wrestool",False)
		self.singleCheck("wine",False)
		self.singleCheck("unzip",False)
		self.singleCheck("7z",False)
		
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
			if(wx.YES == wx.MessageBox(_('Are you sure you want to  want to install {0} package?').format(filename).decode("utf-8","replace"), os.environ["APPLICATION_TITLE"],style=wx.YES_NO | wx.ICON_QUESTION)):
				os.system("bash \"$PLAYONLINUX/bash/playonlinux-pkg\" -i \""+filename+"\" &")
		else:
			playonlinux.open_document(filename,file_extension.lower())

	def MacOpenURL(self, url):
		if(os.environ["POL_OS"] == "Mac" and "playonlinux://" in url):
			wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnLinux"), os.environ["APPLICATION_TITLE"])
		if(os.environ["POL_OS"] == "Linux" and "playonmac://" in url):
			wx.MessageBox(_("You are trying to open a script design for {0}! It might not work as expected").format("PlayOnMac"), os.environ["APPLICATION_TITLE"])
			
		os.system("bash \"$PLAYONLINUX/bash/playonlinux-url_handler\" \""+url+"\" &")
		
	def MacReopenApp(self):
		#sys.exit()
		self.BringWindowToFront()

lng.Lang()
app = PlayOnLinuxApp(redirect=False)
app.MainLoop()
#sys.exit(0)
