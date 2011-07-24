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

import os, getopt, sys, urllib, signal, string, time, webbrowser, gettext, locale, sys, shutil
#locale.setlocale(locale.CODESET,'fr_FR.utf8')

#try:
#	locale.getlocale()
#except:
#	os.environ["LANG"] = "en_US.utf-8"
#locale.setlocale(locale.LC_ALL, '.utf-8')

import wx
	
import lib.Variables as Variables, lib.lng as lng
import guiv3 as gui, install, options, wine_versions as wver, sp, configure, threading

def convertVersionToInt(version): # Codé par MulX en Bash, adapté en python par Tinou
	

	#rajouter pour les vesions de dev -> la version stable peut sortir
	#les personnes qui utilise la version de dev sont quand même informé d'une MAJ
	#ex 3.8.1 < 3.8.2-dev < 3.8.2
	if("dev" in version or "beta" in version or "alpha" in version or "rc" in version):
		version = string.split(version,"-")
		version = version[0]
		versionDev = -5
	else:
		versionDev = 0
		
	version_s = string.split(version,".")
	#on fait des maths partie1 elever au cube et multiplier par 1000
	try:
		versionP1 = int(version_s[0])*int(version_s[0])*int(version_s[0])*1000
	except:
		versionP1 = 0
	try:
		versionP2 = int(version_s[1])*int(version_s[1])*100
	except:
		versionP2 = 0
	try:
		versionP3 = int(version_s[2])*10
	except:
		versionP3 = 0
	return(versionDev + versionP1 + versionP2 + versionP3)

class POLWeb(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.sendToStatusBarStr = ""
		self.Gauge = False
		self.WebVersion = ""
		self.Show = False
	def sendToStatusBar(self, message, gauge):
		self.sendToStatusBarStr = message
		self.Gauge = gauge
		self.Show = True
			
	def LastVersion(self):
		if(os.environ["POL_OS"] == "Mac"):
			fichier_online="version_mac"
		else:
			fichier_online="version2"
		return os.popen('wget -q "$SITE/'+fichier_online+'.php?v=$VERSION" -T 10 -O-','r').read()
	
	def run(self):
		self.WebVersion = self.LastVersion()
		
		if(self.WebVersion == ""):
			self.sendToStatusBar(_(os.environ["APPLICATION_TITLE"]+" website is unavailable. Please check your connexion"), False)
		else:
			self.sendToStatusBar(_("Refreshing "+os.environ["APPLICATION_TITLE"]), True)
			os.system("bash \""+Variables.playonlinux_env+"/bash/pol_update_list\"")
		
		if(convertVersionToInt(os.environ["VERSION"]) < convertVersionToInt(self.WebVersion)):
			self.sendToStatusBar(_("An updated version of "+os.environ["APPLICATION_TITLE"]+" is available")+" ("+self.WebVersion+")",False)
		else:
			self.Show = False

		    
class MainWindow(wx.Frame):
  def __init__(self,parent,id,title):
	wx.Frame.__init__(self, parent, 1000, title, size = (430, 430))
	self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
	self.timer = wx.Timer(self, 1)
	self.images = wx.ImageList(32, 32)

	self.updater = POLWeb()
	self.updater.start()
	
	self.list_game = wx.TreeCtrl(self, 105, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)	
	self.list_game.SetSpacing(0);
	self.list_game.SetImageList(self.images)

	
	self.oldreload = ""	
	self.oldimg = ""
	
	self.filemenu = wx.Menu()
	self.filemenu.Append(wx.ID_OPEN, _("Run"))
	self.filemenu.Append(wx.ID_ADD, _("Install"))
	self.filemenu.Append(wx.ID_DELETE, _("Remove"))
	self.filemenu.AppendSeparator()
	self.filemenu.Append(216, _("Donate"))
	self.filemenu.Append(wx.ID_EXIT, _("Exit"))

	self.expertmenu = wx.Menu()

	self.winever_item = wx.MenuItem(self.expertmenu, 107, _("Manage Wine versions"))
	self.winever_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/wine.png"))
	self.expertmenu.AppendItem(self.winever_item)

	self.wineprefix_item = wx.MenuItem(self.expertmenu, 111, _("Manage virtual drives"))
	self.wineprefix_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/prefix-manager.png"))
	self.expertmenu.AppendItem(self.wineprefix_item)

	self.expertmenu.AppendSeparator()

	self.run_item = wx.MenuItem(self.expertmenu, 108, _("Run a local script"))
	self.run_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/run.png"))
	self.expertmenu.AppendItem(self.run_item)
		
	self.wineserv_item = wx.MenuItem(self.expertmenu, 115, _("Close all "+os.environ["APPLICATION_TITLE"]+" software"))
	self.wineserv_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/wineserver.png"))
	self.expertmenu.AppendItem(self.wineserv_item)

	self.expertmenu.AppendSeparator()

	self.polshell_item = wx.MenuItem(self.expertmenu, 109, _(os.environ["APPLICATION_TITLE"]+" console"))
	self.polshell_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/polshell.png"))
	self.expertmenu.AppendItem(self.polshell_item)
	
	self.bug_item = wx.MenuItem(self.expertmenu, 110, _("Report a bug"))
	self.bug_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/bug.png"))
	self.expertmenu.AppendItem(self.bug_item)
	

	self.optionmenu = wx.Menu()

#	self.option_item = wx.MenuItem(self.expertmenu, 210, _("General"))
#	self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/input-gaming.png"))
#	self.optionmenu.AppendItem(self.option_item)

	self.option_item = wx.MenuItem(self.expertmenu, 211, _("Internet"))
	self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/internet-web-browser.png"))
	self.optionmenu.AppendItem(self.option_item)

	#self.option_item = wx.MenuItem(self.expertmenu, 212, _("Environment"))
	#self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/user-desktop.png"))
	#self.optionmenu.AppendItem(self.option_item)

	#self.option_item = wx.MenuItem(self.expertmenu, 213, _("System"))
	#self.option_item.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/application-x-executable.png"))
	#self.optionmenu.AppendItem(self.option_item)

	
	self.help_menu = wx.Menu()
	self.help_menu.Append(wx.ID_ABOUT, "About "+os.environ["APPLICATION_TITLE"])

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
	self.jauge_update = wx.Gauge(self.sb, -1, 100, (300, hauteur), size=(100,16))
	self.jauge_update.Pulse()
	self.jauge_update.Hide()
	self.SetStatusBar(self.sb)

	#self.helpmenu = wx.MenuItem()
	#self.helpmenu.Append(wx.ID_ABOUT, _("About"))

	self.menubar = wx.MenuBar()
	self.menubar.Append(self.filemenu, _("File"))
	self.menubar.Append(self.expertmenu, _("Tools"))
	self.menubar.Append(self.optionmenu, _("Settings"))
	self.menubar.Append(self.pluginsmenu, _("Plugins"))
	self.menubar.Append(self.help_menu, "&Help")
	
	#self.menubar.Append(self.help_menu, _("About"))
	self.SetMenuBar(self.menubar)
	iconSize = (32,32)

	self.toolbar = self.CreateToolBar(wx.TB_TEXT)
	self.toolbar.SetToolBitmapSize(iconSize)
	self.toolbar.AddLabelTool(wx.ID_OPEN, _("Run"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/run.png"))
	self.toolbar.AddSeparator()
	self.toolbar.AddLabelTool(wx.ID_ADD, _("Install"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/install.png"))
	self.toolbar_remove = self.toolbar.AddLabelTool(wx.ID_DELETE, _("Remove"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/delete.png"))
	#self.toolbar.AddLabelTool(120, _("CD-ROM"), wx.Bitmap(Variables.playonlinux_env+"/etc/menu/cdrom.png"))
	
	self.toolbar.AddSeparator()
	self.toolbar.AddLabelTool(121, _("Configure"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/configure.png"))
	self.toolbar.AddLabelTool(122, _("Shortcut"), wx.Bitmap(Variables.playonlinux_env+"/resources/images/toolbar/package.png"))

	#self.toolbar.DoMenuUpdate(self.toolbar)
	self.toolbar.Realize()
	self.Reload(self)
	wx.EVT_MENU(self, wx.ID_OPEN,  self.Run)
	wx.EVT_MENU(self, wx.ID_ADD,  self.InstallMenu)
	wx.EVT_MENU(self, wx.ID_ABOUT,  self.About)
	wx.EVT_MENU(self,  wx.ID_EXIT,  self.ClosePol)
	wx.EVT_MENU(self,  wx.ID_REFRESH,  self.UpdatePol)
	wx.EVT_MENU(self,  wx.ID_DELETE,  self.UninstallGame)
	

	# Expert
	wx.EVT_MENU(self, 101,  self.Reload)
	wx.EVT_MENU(self, 107,  self.WineVersion)
	wx.EVT_MENU(self, 108,  self.Executer)
	wx.EVT_MENU(self, 109,  self.PolShell)
	wx.EVT_MENU(self, 110,  self.BugReport)
	wx.EVT_MENU(self, 111,  self.ManagePrefix)
	wx.EVT_MENU(self, 115,  self.killall)
	wx.EVT_MENU(self, 120,  self.Autorun)
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
	#self.sb.Hide()
	
  def StatusRead(self):
	self.sb.SetStatusText(self.updater.sendToStatusBarStr, 0)
	if(self.updater.Gauge == True):
		self.jauge_update.Pulse()
		self.jauge_update.Show()
	else:
		self.jauge_update.Hide()

	if(self.updater.Show == True):
		self.sb.Show()
	else:
		self.sb.Hide()	
		
  def RMBInGameList(self, event):
	self.GameListPopUpMenu = wx.Menu()

	self.ConfigureWine = wx.MenuItem(self.GameListPopUpMenu, 230, _("Configure Wine"))
	self.ConfigureWine.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/run.png"))
	self.GameListPopUpMenu.AppendItem(self.ConfigureWine)

	self.RegistryEditor = wx.MenuItem(self.GameListPopUpMenu, 231, _("Registry Editor"))
	self.RegistryEditor.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/regedit.png"))
	self.GameListPopUpMenu.AppendItem(self.RegistryEditor)

	self.GotoAppDir = wx.MenuItem(self.GameListPopUpMenu, 232, _("Open the application's directory"))
	self.GotoAppDir.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/user-desktop.png"))
	self.GameListPopUpMenu.AppendItem(self.GotoAppDir)

	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 233, _("Set the icon"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/playonlinux16.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 234, _("Remove"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/options.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

	self.ChangeIcon = wx.MenuItem(self.GameListPopUpMenu, 235, _("Close this application"))
	self.ChangeIcon.SetBitmap(wx.Bitmap(Variables.playonlinux_env+"/etc/menu/wineserver.png"))
	self.GameListPopUpMenu.AppendItem(self.ChangeIcon)

	self.PopupMenu(self.GameListPopUpMenu, event.GetPoint())
    #if(len(sys.argv) >= 1):

    #wx.MessageBox(str(sys.argv), "PlayOnLinux", wx.OK)


  def RWineConfigurator(self, event):
        self.RConfigure(_("Configure Wine"), "nothing")

  def RKill(self, event):
        self.RConfigure(_("KillApp"), "nothing")

  def RRegistryEditor(self, event):
        self.RConfigure(_("Registry Editor"), "nothing")

  def run_plugin(self, event):
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
	plugin=self.plugin_list[event.GetId()-300]
	try :
		os.system("bash \""+Variables.playonlinux_rep+"/plugins/"+plugin+"/scripts/menu\" \""+game_exec+"\"&")
	except : 
		print("bash \""+Variables.playonlinux_rep+"/plugins/"+plugin+"/scripts/menu\" "+game_exec+"&")
		
  def GoToAppDir(self, event):
		game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
		self.read = open(Variables.playonlinux_rep+"configurations/installed/"+game_exec,"r").readlines()

		if not len(self.read):
			return

		self.i = 0;
		while(self.i < len(self.read)):
			if("cd \"" in self.read[self.i]):
				break
			self.i += 1

		if len(self.read) == (self.i):
			return

		AppDir = self.read[self.i][3:]
		if AppDir != "":
			if(os.environ["POL_OS"] == "Mac"):
				os.system("open "+AppDir)
			else:
				os.system("xdg-open "+AppDir)
			
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
	game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
	self.read = open(Variables.playonlinux_rep+"configurations/installed/"+game_exec,"r").readlines()
	self.i = 0;
	self.wine_present = False;
	while(self.i < len(self.read)):
		if("wine " in self.read[self.i]):
			self.wine_present = True;
		self.i += 1

  def donate(self, event):
	if(os.environ["POL_OS"] == "Mac"):
		webbrowser.open("http://www.playonmac.com/en/donate.html")
	else:
		webbrowser.open("http://www.playonlinux.com/en/donate.html")
	
  def Reload(self, event):
	 self.games = os.listdir(Variables.playonlinux_rep+"configurations/installed/")
	 self.games.sort()
	 try:
	 	self.games.remove(".DS_Store")
	 except:
	 	pass
	 self.list_game.DeleteAllItems()
	 self.images.RemoveAll()
	 root = self.list_game.AddRoot("")
	 self.i = 0
	 for game in self.games: #METTRE EN 32x32
		if(os.path.exists(Variables.playonlinux_rep+"/icones/32/"+game)):
			file_icone = Variables.playonlinux_rep+"/icones/32/"+game
		else:
			file_icone = Variables.playonlinux_env+"/etc/playonlinux32.png"

		try:
			self.images.Add(wx.Bitmap(file_icone))
		except:
			pass
		item = self.list_game.AppendItem(root, game, self.i)
		self.i += 1
	

  def RConfigure(self, function_to_run, firstargument):
		"""Starts polconfigurator remotely."""
		game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
		if(game_exec != ""):
			os.system("bash \""+Variables.playonlinux_env+"/bash/polconfigurator\" \""+game_exec+"\" \""+function_to_run+"\" \""+firstargument+"\"&")
	
	    
	
  def Options(self, event):
    print("Running options")
    onglet=event.GetId()-210
    self.optionFrame = options.MainWindow(self, -1, _(os.environ["APPLICATION_TITLE"]+" Settings"), onglet)
    self.optionFrame.Center(wx.BOTH)
    self.optionFrame.Show(True)

  def killall(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/killall\"&")

  def Executer(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/expert/Executer\"&")

  def BugReport(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/bug_report\"&")

  def ManagePrefix(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/prefix_manager\" &")

  def PolShell(self, event):
    #Variables.run_x_server()
    os.system("bash \""+Variables.playonlinux_env+"/bash/expert/PolShell\"&")

  def Configure(self, event):
    game_exec = self.list_game.GetItemText(self.list_game.GetSelection()) 
    if(game_exec == ""):
		wx.MessageBox(_("Please select a program."), os.environ["APPLICATION_TITLE"], wx.OK)
    else:
		configureFrame = configure.MainWindow(None, -1, game_exec+_(" configuration"),game_exec)
		#self.SetTopWindow(installFrame)
		configureFrame.Center(wx.BOTH)
		configureFrame.Show(True)

    #os.system("bash \""+Variables.playonlinux_env+"/bash/polconfigurator\" \""+game_exec+"\"&")

  def Package(self, event):
    game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
    os.system("bash \""+Variables.playonlinux_env+"/bash/make_shortcut\" \""+game_exec+"\"&")

  def UninstallGame(self, event):
    game_exec = self.list_game.GetItemText(self.list_game.GetSelection())
    os.system("bash \""+Variables.playonlinux_env+"/bash/uninstall\" \""+game_exec+"\"&")


  def AutoReload(self, event):
	self.StatusRead()
	fichier_index = os.environ["REPERTOIRE"]+"/configurations/guis/index_"+os.environ["POL_ID"]
	#print(fichier_index)
	message = open(fichier_index,'r').read()
	message = string.split(message, "\n")
	if(message[0] == "Open"):
		self.frame = gui.POL_SetupFrame(os.environ["APPLICATION_TITLE"],message[1].replace("\n",""),message[2].replace("\n",""),message[3].replace("\n",""),message[4].replace("\n",""))
		self.frame.Center(wx.BOTH)
		self.frame.Show(True)
		open(fichier_index,'w').write("Wait")

	reload = os.listdir(Variables.playonlinux_rep+"/configurations/installed")
	if(reload != self.oldreload):
		self.Reload(self)
		self.oldreload = reload

	reloadimg = os.listdir(Variables.playonlinux_rep+"/icones/32")
	if(reloadimg != self.oldimg):
		self.Reload(self)
		self.oldimg = reloadimg
   

  def InstallMenu(self, event):
    installFrame = install.InstallWindow(None, -1, os.environ["APPLICATION_TITLE"]+" Install menu")
    #self.SetTopWindow(installFrame)
    installFrame.Center(wx.BOTH)
    installFrame.Show(True)
	
    
  def UpdatePol(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/check_maj\"&")
  
  def Autorun(self, event):
    os.system("bash \""+Variables.playonlinux_env+"/bash/autorun\"&")

  def WineVersion(self, event):
    wversion = wver.MainWindow(None, -1, os.environ["APPLICATION_TITLE"]+" wine versions manager")
    wversion.Center(wx.BOTH)
    wversion.Show(True)
	#os.system("bash \""+Variables.playonlinux_env+"/bash/wineversion\"&")

  def Run(self, event):
    game_exec = self.list_game.GetItemText(self.list_game.GetSelection()).encode("utf-8")
    if(game_exec != ""):
		os.system("bash "+Variables.playonlinux_env+"/bash/run_app \""+game_exec+"\"&")
		#os.system("cd \""+Variables.playonlinux_rep+"/configurations/installed/\"  && bash \""+game_exec+"\"&")


  def ClosePol(self, event):
    if(wx.YES == wx.MessageBox(_("Are you sure you want to close all "+os.environ["APPLICATION_TITLE"]+" Windows ?").decode("utf-8"), style=wx.YES_NO | wx.ICON_QUESTION)):
		os.remove(Variables.playonlinux_rep+"/configurations/guis/index_"+os.environ["POL_ID"])
		os._exit(0)
    return None
    
  def About(self, event):
    self.aboutBox = wx.AboutDialogInfo()
    if(os.environ["POL_OS"] == "Linux"):
    	self.aboutBox.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))


    self.aboutBox.SetName(os.environ["APPLICATION_TITLE"])
    self.aboutBox.SetVersion(Variables.version)
    self.aboutBox.SetDescription(_("Run your Windows programs on "+os.environ["POL_OS"]+" !"))
    self.aboutBox.SetCopyright(_("(C) PlayOnLinux and PlayOnMac team 2011\nUnder GPL licence version 3"))
    self.aboutBox.AddDeveloper(_("Developer and Website: ")+"Tinou (Pâris Quentin), MulX (Petit Aymeric)")
    self.aboutBox.AddDeveloper(_("Scriptors: ")+"GNU_Raziel")
    self.aboutBox.AddDeveloper(_("Packager: ")+"MulX (Petit Aymeric), Tinou (Pâris Quentin)")
    self.aboutBox.AddDeveloper(_("Icons:")+"Faenza-Icons http://tiheum.deviantart.com/art/Faenza-Icons-173323228")
    self.aboutBox.AddDeveloper(_("The following people contributed to this program: ")+"kiplantt, Salvatos, Minchul")
    self.aboutBox.AddTranslator(_("Translation made on Launchpad:"))
    self.aboutBox.AddTranslator("https://translations.launchpad.net/playonlinux/")

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
		for f in  sys.argv[1:]:
			self.MacOpenFile(f)
			if(".exe" in f or ".EXE" in f):
				exe_present = True
			close = True
			
		if(close == True and exe_present == False):
			sys.exit()
			
		self.SetClassName(os.environ["APPLICATION_TITLE"])
		self.SetAppName(os.environ["APPLICATION_TITLE"])
		#self.icon = wx.TaskBarIcon()
		#self.icon.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonmac.png", wx.BITMAP_TYPE_ANY))
		self.frame = MainWindow(None, -1, os.environ["APPLICATION_TITLE"])
		self.SetTopWindow(self.frame)
		self.frame.Center(wx.BOTH)
		self.frame.Show(True)
		
		return True
	
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
			#	wx.MessageBox(content[i], "PlayOnLinux", wx.OK)
			   	
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
		
		if(file_extension == "exe" or file_extension == "EXE"):
			os.system("bash \"$PLAYONLINUX/bash/run_exe\" \""+filename+"\" &")
			
	def MacReopenApp(self):
		#sys.exit()
		self.BringWindowToFront()


lng.Lang()
#os.system("bash \""+os.environ["PLAYONLINUX"]+"/bash/startup\"")
app = PlayOnLinuxApp(redirect=False)
app.MainLoop()
#sys.exit(0)
