#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Pâris Quentin
# Copyright (C) 2007-2010 PlayOnLinux Team

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

from asyncore import dispatcher
import wxversion, os, getopt, sys, urllib, signal, socket, string
import wx, time
import webbrowser, shutil
import threading, time, codecs
from select import select
#from subprocess import Popen,PIPE

import lib.Variables as Variables
import lib.lng as lng

class getPlugins(threading.Thread):
  def __init__(self):
	threading.Thread.__init__(self)
	self.thread_message = "#WAIT#"
	self.versions = []
	self.start()

  def download(self, game):
	self.getDescription = game
	
  def run(self):
	self.thread_running = True
	while(self.thread_running):
		if(self.thread_message == "get"):
			try :
				url = 'http://mulx.playonlinux.com/wine/linux-i386/LIST'
				req = urllib2.Request(url)
				handle = urllib2.urlopen(req)
				time.sleep(1)
				available_versions = handle.read()
				available_versions = string.split(available_versions,"\n")
				self.i = 0
				self.versions_ = []
				while(self.i < len(available_versions) - 1):
					informations = string.split(available_versions[self.i], ";")
					version = informations[1]
					package = informations[0]
					sha1sum = informations[2]
					if(not os.path.exists(Variables.playonlinux_rep+"/WineVersions/"+version)):
						self.versions_.append(version)
					self.i += 1	
				self.versions_.reverse()
				self.versions = self.versions_[:]

				self.thread_message = "Ok"
			except :
				time.sleep(1)
				self.thread_message = "Err"
				self.versions = ["Wine packages website is unavailable"]
		else:
			time.sleep(0.2)


class Onglets(wx.Notebook):
	# Classe dérivée du wx.Notebook
	def __init__(self, parent):
		if(os.environ["POL_OS"] == "Mac"):
			self.fontTitle = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
			self.caption_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
		else :
			self.fontTitle = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
			self.caption_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
		
		
		self.notebook = wx.Notebook.__init__(self, parent, -1)
		self.images_onglets = wx.ImageList(16, 16)
    		self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/input-gaming.png"));
  		self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/internet-group-chat.png"));
  		self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/internet-web-browser.png"));
  		self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/user-desktop.png"));
  		self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/application-x-executable.png"));
		self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/package-x-generic.png"));
   		self.SetImageList(self.images_onglets)

	
	def browser_test(self, event):
		if(self.Navigator.GetValue() == "Default"):
			webbrowser.open("http://www.playonlinux.com")	
		else:
			os.system(self.Navigator.GetValue()+" http://www.playonlinux.com &")

	def term_test(self, event):
		os.system("bash "+Variables.playonlinux_env+"/bash/terminals/"+self.Term.GetValue()+" sleep 2 &")

	def Internet(self, nom):
		self.panelInternet = wx.Panel(self, -1)

		if(os.path.exists(Variables.playonlinux_rep+"/configurations/options/offline")):
			if(open(Variables.playonlinux_rep+"/configurations/options/offline",'r').read() == '1'):
				self.OffLineCheck.SetValue(1)
		
		self.ProxySettings = wx.StaticText(self.panelInternet, -1, _("Proxy configuration"), (0,0), wx.DefaultSize)
		self.ProxySettings.SetFont(self.fontTitle)
		
		proxy_settings = {}
		
		proxy_settings['PROXY_ENABLED'] = "0"
		proxy_settings['PROXY_ADRESS'] = ""
		proxy_settings["PROXY_PORT"] = "8080"
		proxy_settings["PROXY_LOGIN"] = ""
		proxy_settings["PROXY_PASS"] = ""
		
		if(os.path.exists(Variables.playonlinux_rep+"/configurations/options/proxy")):
			proxy = open(Variables.playonlinux_rep+"/configurations/options/proxy","r").readlines()
			self.i = 0
			
			while(self.i < len(proxy)):
				line_parsed = string.split(proxy[self.i].replace("\n","").replace("\r",""),"=")
				#print line_parsed[0] + " " + line_parsed[1]
				proxy_settings[line_parsed[0]] = line_parsed[1]
				self.i += 1
		
		self.ProxyCheck = wx.CheckBox(self.panelInternet, 120, _("Set a proxy"),pos=(10,30))
		self.ProxyCheck.SetValue(int(proxy_settings['PROXY_ENABLED']))

		self.ProxyTxtAdresse = wx.StaticText(self.panelInternet, -1, _("Proxy address"), (10,60), wx.DefaultSize)
		self.ProxyAdresse = wx.TextCtrl(self.panelInternet, -1, proxy_settings["PROXY_ADRESS"], pos=(20,80),size=(300,27))
		
		self.ProxyTxtPort = wx.StaticText(self.panelInternet, -1, _("Proxy port"), (10,120), wx.DefaultSize)
		self.ProxyPort = wx.TextCtrl(self.panelInternet, -1, proxy_settings["PROXY_PORT"], pos=(20,140),size=(80,27))

		self.ProxyTxtLogin = wx.StaticText(self.panelInternet, -1, _("Proxy login"), (10,180), wx.DefaultSize)
		self.ProxyLogin = wx.TextCtrl(self.panelInternet, -1, proxy_settings["PROXY_LOGIN"], pos=(20,200),size=(300,27))

		self.ProxyTxtPass = wx.StaticText(self.panelInternet, -1, _("Proxy password"), (10,240), wx.DefaultSize)
		self.ProxyPass = wx.TextCtrl(self.panelInternet, -1, proxy_settings["PROXY_PASS"], pos=(20,260),size=(300,27), style=wx.TE_PASSWORD)
		self.AddPage(self.panelInternet, nom, imageId=2)
		wx.EVT_CHECKBOX(self, 120, self.proxy_enable)
		self.proxy_enable(self)

	def proxy_enable(self, event):
		if(self.ProxyCheck.IsChecked() == 1):
			self.ProxyAdresse.Enable(True)
			self.ProxyLogin.Enable(True)
			self.ProxyPass.Enable(True)
			self.ProxyPort.Enable(True)
		else:
			self.ProxyAdresse.Enable(False)
			self.ProxyLogin.Enable(False)
			self.ProxyPass.Enable(False)
			self.ProxyPort.Enable(False)



	def LoadPlugins(self):
		self.pluginlist.DeleteAllItems()
		self.pluginImgList.RemoveAll()
		plugins=os.listdir(Variables.playonlinux_rep+"/plugins/")
		self.i = 0
		
		PluginsRoot = self.pluginlist.AddRoot("")
		plugins.sort()
		while(self.i < len(plugins)):
			self.pluginlist.AppendItem(PluginsRoot, plugins[self.i], self.i)
			if(os.path.exists(Variables.playonlinux_rep+"/plugins/"+plugins[self.i]+"/enabled") == False):
				self.pluginlist.SetItemTextColour(self.pluginlist.GetLastChild(PluginsRoot), wx.Colour(150,150,150))
			self.icon_look_for = Variables.playonlinux_rep+"/plugins/"+plugins[self.i]+"/icon"
			if(os.path.exists(self.icon_look_for)):
				self.pluginImgList.Add(wx.Bitmap(self.icon_look_for))
			else:	
				self.pluginImgList.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/playonlinux16.png"))
			self.i += 1
		self.EnablePlugin.Enable(False)
		self.ConfigurePlugin.Enable(False)
		self.DelPlugin.Enable(False)

	def Plugins(self, nom):
		self.panelPlugins= wx.Panel(self, -1)
		self.panels_buttons_plugins = wx.Panel(self.panelPlugins, -1)

		self.sizerPlugins = wx.BoxSizer(wx.VERTICAL) 
		self.txtPlugin = wx.StaticText(self.panelPlugins, -1, _("Installed plugins"), size=wx.DefaultSize)
		self.txtPlugin.SetFont(self.fontTitle)
		self.pluginlist = wx.TreeCtrl(self.panelPlugins, 220, style=wx.RAISED_BORDER|wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)		
		self.pluginlist.SetSpacing(0)

		self.pluginImgList = wx.ImageList(16,16)

		self.pluginlist.SetImageList(self.pluginImgList)

		

		self.sizerPlugins.Add(self.txtPlugin, 1, wx.EXPAND|wx.ALL, 2)
		self.sizerPlugins.Add(self.pluginlist, 7, wx.EXPAND|wx.ALL, 2)

    		self.sizerPlugins.Add(self.panels_buttons_plugins, 6, wx.EXPAND|wx.ALL, 2)
		
		self.panelPlugins.SetSizer(self.sizerPlugins)
   		self.panelPlugins.SetAutoLayout(True)
		self.AddPlugin = wx.Button(self.panels_buttons_plugins, wx.ID_ADD,  pos=(0,0))
		self.DelPlugin = wx.Button(self.panels_buttons_plugins, wx.ID_REMOVE, pos=(100,0))
		self.ConfigurePlugin = wx.Button(self.panels_buttons_plugins, 212, _("Configure"), pos=(0,38))	
		self.EnablePlugin = wx.Button(self.panels_buttons_plugins, 213, _("Enable"), pos=(100,38))
		self.txtPlugin = wx.StaticText(self.panels_buttons_plugins, -1, _("Choose a plugin"), size=(300,150), pos=(200,5))

		self.LoadPlugins()

		self.AddPage(self.panelPlugins, nom, imageId=5)

		wx.EVT_TREE_SEL_CHANGED(self, 220, self.choose_plugin)
	
		wx.EVT_BUTTON(self, 214, self.disable)
		wx.EVT_BUTTON(self, 213, self.enable)
		wx.EVT_BUTTON(self, 212, self.setup_plug)
		wx.EVT_BUTTON(self, wx.ID_REMOVE, self.delete_plug)
		wx.EVT_BUTTON(self, wx.ID_ADD, self.add_plug)

	def setup_plug(self, event):
		self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
		self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
		os.system("bash \""+self.plugin_path+"/scripts/options\" &")

	def add_plug(self, event):
		self.FileDialog = wx.FileDialog(self)
		self.FileDialog.SetDirectory("~")
		self.FileDialog.SetWildcard("POL Packages (*.pol)|*.pol")
        	self.FileDialog.ShowModal()
        	if(self.FileDialog.GetPath() != ""):
			if(wx.YES == wx.MessageBox(_("Are you sure you want to install: ").decode("utf-8")+self.FileDialog.GetPath()+"?", style=wx.YES_NO | wx.ICON_QUESTION)):
	      			os.system("bash \""+Variables.playonlinux_env+"/playonlinux-pkg\" -i \""+self.FileDialog.GetPath().encode('utf-8')+"\"")
				self.LoadPlugins()
        	self.FileDialog.Destroy()

	def delete_plug(self, event):
		self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
		self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
   	        if(wx.YES == wx.MessageBox(_("Are you sure you want to delete: ").decode("utf-8")+self.current_plugin+"?", style=wx.YES_NO | wx.ICON_QUESTION)):
			shutil.rmtree(self.plugin_path)
			self.LoadPlugins()
	def disable(self, event):
		self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
		self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
		os.remove(self.plugin_path+"/enabled")
		self.LoadPlugins()

	def enable(self, event):
		self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
		self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
		enab=open(self.plugin_path+"/enabled",'w')
		enab.close()
		self.LoadPlugins()

	def choose_plugin(self, event):
		self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
		self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
		if(os.path.exists(self.plugin_path+"/enabled")):
			self.EnablePlugin.Destroy()
			self.EnablePlugin = wx.Button(self.panels_buttons_plugins, 214, _("Disable"), pos=(100,38))
		else:
			self.EnablePlugin.Destroy()
			self.EnablePlugin = wx.Button(self.panels_buttons_plugins, 213, _("Enable"), pos=(100,38))

		if(os.path.exists(self.plugin_path+"/scripts/options")):
			self.ConfigurePlugin.Enable(True)
		else:
			self.ConfigurePlugin.Enable(False)
	
		if(os.path.exists(self.plugin_path+"/description")):	
			self.txtPlugin.Destroy()
			self.txtPlugin = wx.StaticText(self.panels_buttons_plugins, -1, open(self.plugin_path+"/description","r").read(), size=(285,150), pos=(200,5))

		self.DelPlugin.Enable(True)

	def glxinfo(self, event):
		glx = os.popen("glxinfo", "r").read()
		self.txtGLX.SetValue(glx)

	def xorg(self, event):
		glx = open("/etc/X11/xorg.conf", "r").read()
		self.txtGLX.SetValue(glx)

	def glxgears(self, event):
		self.result = os.popen("glxgears", "r").read()
		self.txtGLX.SetValue(self.result)
	
	def system_info(self, event):
		self.txtGLX.SetValue(os.popen("bash \""+Variables.playonlinux_env+"/bash/system_info\" &", "r").read())

	def SupprimePage(self, index):
		self.DeletePage(index)
			

class MainWindow(wx.Frame):
  def __init__(self,parent,id,title,onglet):
    wx.Frame.__init__(self, parent, -1, title, size = (505, 550), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
    self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
    self.panelFenp = wx.Panel(self, -1)
    self.panels_buttons = wx.Panel(self.panelFenp, -1)
    self.Apply = wx.Button(self.panels_buttons, wx.ID_APPLY, _("Apply"), pos=(400,0))
    self.Close = wx.Button(self.panels_buttons, wx.ID_CLOSE, _("Cancel"), pos=(305,0))
    self.sizer = wx.BoxSizer(wx.VERTICAL)   
    self.onglets = Onglets(self.panelFenp)

    self.sizer.Add(self.onglets, 10, wx.EXPAND|wx.ALL, 2)
    self.sizer.Add(self.panels_buttons, 1, wx.EXPAND|wx.ALL, 2)

    #self.onglets.General(_("General"))
    self.onglets.Internet(_("Internet"))
    #self.onglets.Wine(_("Environment"))
    #self.onglets.System(_("System"))
    self.onglets.Plugins(_("Plugins"))
    try:
		self.onglets.SetSelection(onglet)
    except:
		pass

    self.panelFenp.SetSizer(self.sizer)
    self.panelFenp.SetAutoLayout(True)
    wx.EVT_BUTTON(self, wx.ID_APPLY, self.apply_settings)
    wx.EVT_BUTTON(self, wx.ID_CLOSE, self.app_Close)

  def app_Close(self, event):
    self.Destroy()

  def apply_settings(self, event):
    if(self.onglets.ProxyAdresse.GetValue().replace("http://","") and self.onglets.ProxyPort.GetValue()):
	    self.chaine = "PROXY_ENABLED="+str(int(self.onglets.ProxyCheck.IsChecked()))+"\nPROXY_ADRESS="+self.onglets.ProxyAdresse.GetValue().replace("http://","")+"\n"+"PROXY_PORT="+self.onglets.ProxyPort.GetValue()+"\n"
	    if(self.onglets.ProxyLogin.GetValue() and self.onglets.ProxyPass.GetValue()):
		self.chaine += "PROXY_LOGIN="+self.onglets.ProxyLogin.GetValue()+"\n"+"PROXY_PASS="+self.onglets.ProxyPass.GetValue()+"\n"
    else:
	    self.chaine=""

	   
    open(Variables.playonlinux_rep+"/configurations/options/proxy","w").write(self.chaine)

    wx.MessageBox(_("You must restart PlayOnLinux for the changes to take effect."), "PlayOnLinux", wx.OK)
    self.Destroy()

