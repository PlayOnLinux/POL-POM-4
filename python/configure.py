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

import wine_versions
import lib.Variables as Variables
import lib.lng as lng


class Onglets(wx.Notebook):
	# Classe dérivée du wx.Notebook
	def __init__(self, parent, s_title):
		self.notebook = wx.Notebook.__init__(self, parent, -1)
		self.s_title = s_title
		self.changing = False
		
	def ChangeTitle(self, new_title):
		self.s_title = new_title
		self.general_elements["name"].SetValue(new_title)
		self.changing = True

	def winebash(self, command):
		os.system("bash "+Variables.playonlinux_env+"/bash/winebash \""+self.s_title+"\" "+command+" &")
		
	def evt_winecfg(self, event):
		self.winebash("winecfg")
		
	def evt_regedit(self, event):
		self.winebash("regedit")

	def evt_cmd(self, event):
		self.winebash("wineconsole cmd")

	def evt_taskmgr(self, event):
		self.winebash("taskmgr")
		
	def evt_wineboot(self, event):
		self.winebash("wineboot")

	def evt_killall(self, event):
		self.winebash("wineserver -k")
	
	def evt_config(self, event):
		os.system("bash \""+Variables.playonlinux_rep+"/configurations/configurators/"+self.s_title+"\" &")
				
	def install_package(self, event):
		os.system("bash "+Variables.playonlinux_env+"/bash/installpolpackages \""+self.s_title+"\" POL_Install_"+self.available_packages_[self.Menu.GetSelection()]+" &")
		
	def AddGeneralChamp(self, title, shortname, value, num):
		self.general_elements[shortname+"_text"] = wx.StaticText(self.panelGeneral, -1, title,pos=(15,315+num*40))
		self.general_elements[shortname] = wx.TextCtrl(self.panelGeneral, 200+num, value, pos=(300,315+num*40), size=(150,20))
	#	self.general_elements[shortname].SetValue(value)

	def AddGeneralElement(self, title, shortname, elements, wine, num):
		elements.insert(0,"System")
		wine.insert(0,"System")
		self.general_elements[shortname+"_text"] = wx.StaticText(self.panelGeneral, -1, title,pos=(15,319+num*40))
		
		self.general_elements[shortname] = wx.ComboBox(self.panelGeneral, 200+num, style=wx.CB_READONLY,pos=(300,315+num*40))
		self.general_elements[shortname].AppendItems(elements)
		self.general_elements[shortname].SetValue(elements[0])

	def Get_versions(self):
		installed_versions = os.listdir(Variables.playonlinux_rep+"/WineVersions/")
		installed_versions.sort(key=wine_versions.keynat)
		installed_versions.reverse()
		try:
			installed_versions.remove("installed")
		except:
			pass
		return installed_versions
		
	def General(self, nom):
		self.panelGeneral = wx.Panel(self, -1)
		self.AddPage(self.panelGeneral, nom)
		self.general_elements = {}
		# Les polices
		if(os.environ["POL_OS"] == "Mac"):
			self.fontTitle = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
			self.caption_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
		else :
			self.fontTitle = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
			self.caption_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)

		self.txtGeneral = wx.StaticText(self.panelGeneral, -1, _("General"), (10,10), wx.DefaultSize)
		self.txtGeneral.SetFont(self.fontTitle)
		
		self.winecfg_image = wx.Image( Variables.playonlinux_env+"/resources/images/configure/winecfg.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.winecfg = wx.BitmapButton(self.panelGeneral, id=100, bitmap=self.winecfg_image,pos=(30, 50), size = (self.winecfg_image.GetWidth()+5, self.winecfg_image.GetHeight()+5))
		self.winecfg_texte = wx.StaticText(self.panelGeneral, -1, _("Configure Wine"), (30,156), (115,30),wx.ALIGN_CENTER)
		self.winecfg_texte.Wrap(110)
		self.winecfg_texte.SetFont(self.caption_font)
		
		self.regedit_image = wx.Image( Variables.playonlinux_env+"/resources/images/configure/regedit.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.regedit = wx.BitmapButton(self.panelGeneral, id=101, bitmap=self.regedit_image,pos=(166, 50), size = (self.regedit_image.GetWidth()+5, self.regedit_image.GetHeight()+5))
		self.regedit_texte = wx.StaticText(self.panelGeneral, -1, _("Registry Editor"), (166,156), (115,30),wx.ALIGN_CENTER)
		self.regedit_texte.Wrap(110)
		self.regedit_texte.SetFont(self.caption_font)
		
		
		self.wineboot_image = wx.Image( Variables.playonlinux_env+"/resources/images/configure/wineboot.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.wineboot = wx.BitmapButton(self.panelGeneral, id=102, bitmap=self.wineboot_image,pos=(302, 50), size = (self.wineboot_image.GetWidth()+5, self.wineboot_image.GetHeight()+5))		
		self.wineboot_texte = wx.StaticText(self.panelGeneral, -1, _("Windows reboot"), (302,156), (130,30),wx.ALIGN_CENTER)
		self.wineboot_texte.Wrap(110)
		self.wineboot_texte.SetFont(self.caption_font)

		self.cmd_image = wx.Image( Variables.playonlinux_env+"/resources/images/configure/cmd.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.cmd = wx.BitmapButton(self.panelGeneral, id=103, bitmap=self.cmd_image,pos=(30, 196), size = (self.cmd_image.GetWidth()+5, self.cmd_image.GetHeight()+5))
		self.cmd_texte = wx.StaticText(self.panelGeneral, -1, _("Command prompt"), (30,302), (115,30),wx.ALIGN_CENTER)
		self.cmd_texte.Wrap(115)
		self.cmd_texte.SetFont(self.caption_font)

		self.taskmgr_image = wx.Image( Variables.playonlinux_env+"/resources/images/configure/taskmgr.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.taskmgr = wx.BitmapButton(self.panelGeneral, id=104, bitmap=self.taskmgr_image,pos=(166, 196), size = (self.taskmgr_image.GetWidth()+5, self.taskmgr_image.GetHeight()+5))
		self.taskmgr_texte = wx.StaticText(self.panelGeneral, -1, _("Task manager"), (166,302), (115,30),wx.ALIGN_CENTER)
		self.taskmgr_texte.Wrap(110)
		self.taskmgr_texte.SetFont(self.caption_font)


		self.killall_image = wx.Image( Variables.playonlinux_env+"/resources/images/configure/killall.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.killall = wx.BitmapButton(self.panelGeneral, id=105, bitmap=self.killall_image,pos=(302, 196), size = (self.killall_image.GetWidth()+5, self.killall_image.GetHeight()+5))		
		self.killall_texte = wx.StaticText(self.panelGeneral, -1, _("Kill processes"), (302,302), (130,30),wx.ALIGN_CENTER)
		self.killall_texte.Wrap(110)
		self.killall_texte.SetFont(self.caption_font)
		
		self.AddGeneralChamp("Name","name",self.s_title,1)
		self.AddGeneralElement("Wine version","wineversion",self.Get_versions(),self.Get_versions(),2)
		
		
		self.configurator_title = wx.StaticText(self.panelGeneral, -1, "", (10,430), wx.DefaultSize)
		self.configurator_title.SetFont(self.fontTitle)
		self.configurator_button = wx.Button(self.panelGeneral, 106, _("Run configuration wizard"), pos=(15,460))
		
		
		wx.EVT_BUTTON(self, 100, self.evt_winecfg)
		wx.EVT_BUTTON(self, 101, self.evt_regedit)
		wx.EVT_BUTTON(self, 102, self.evt_wineboot)
		wx.EVT_BUTTON(self, 103, self.evt_cmd)
		wx.EVT_BUTTON(self, 104, self.evt_taskmgr)
		wx.EVT_BUTTON(self, 105, self.evt_killall)
		wx.EVT_BUTTON(self, 106, self.evt_config)
		
		wx.EVT_TEXT(self, 201, self.setname)
		wx.EVT_COMBOBOX(self, 202, self.assign)
		
	def Packages(self, nom):
		self.panelPackages = wx.Panel(self, -1)
		self.txtPackages = wx.StaticText(self.panelPackages, -1, _(nom), (10,10), wx.DefaultSize)
		self.txtPackages.SetFont(self.fontTitle)

		self.Menu = wx.ListBox(self.panelPackages, 99, pos=(15,45),size=(430,470), style=Variables.widget_borders)
		self.PackageButton = wx.Button(self.panelPackages, 98, _("Install"), pos=(15,530))
		
		try : 
			self.available_packages = open(Variables.playonlinux_rep+"/configurations/listes/POL_Functions","r").read()
			self.available_packages = string.split(self.available_packages,"/")
			self.available_packages_ = []
			for key in self.available_packages:
				if("POL_Install" in key):
					self.available_packages_.append(key.replace("POL_Install_",""))
			self.available_packages.sort()
			self.Menu.InsertItems(self.available_packages_,0)
			self.Menu.Select(0)
		except : # File does not exits ; it will be created when pol is updated
			pass 
		#$REPERTOIRE/configurations/listes/
		wx.EVT_LISTBOX_DCLICK(self, 99, self.install_package)
		wx.EVT_BUTTON(self, 98, self.install_package)
		
		self.AddPage(self.panelPackages, nom)
	
	def change_Direct3D_settings(self, param):
		os.system("bash "+Variables.playonlinux_env+"/bash/POL_Command \""+self.s_title+"\" POL_Wine_Direct3D "+param+" "+self.display_elements[param].GetValue()+" &")

	def change_DirectInput_settings(self, param):
		os.system("bash "+Variables.playonlinux_env+"/bash/POL_Command \""+self.s_title+"\" POL_Wine_DirectInput "+param+" "+self.display_elements[param].GetValue()+" &")
			
	def get_current_settings(self, param):
		value = os.popen("bash "+Variables.playonlinux_env+"/bash/POL_Command \""+self.s_title+"\" POL_Wine_GetRegValue "+param,'r').read()
		self.display_elements[param].SetValue(value)
		
	def UpdateValues(self):
		self.get_current_settings("UseGLSL")
		self.get_current_settings("DirectDrawRenderer")
		self.get_current_settings("VideoMemorySize")
		self.get_current_settings("OffscreenRenderingMode")
		self.get_current_settings("RenderTargetModeLock")
		self.get_current_settings("Multisampling")
		self.get_current_settings("StrictDrawOrdering")
		self.get_current_settings("MouseWarpOverride")
		if(os.path.exists(Variables.playonlinux_rep+"configurations/configurators/"+self.s_title)):
			self.configurator_title.Show()
			self.configurator_button.Show()
		else:
			self.configurator_title.Hide()
			self.configurator_button.Hide()	
		self.configurator_title.SetLabel(self.s_title+" specific configuration")
			
	def change_settings(self, event):
		param = event.GetId()
		if(param == 301):
			self.change_Direct3D_settings("UseGLSL")
		if(param == 302):
			self.change_Direct3D_settings("DirectDrawRenderer")
		if(param == 303):
			self.change_Direct3D_settings("VideoMemorySize")
		if(param == 304):
			self.change_Direct3D_settings("OffscreenRenderingMode")
		if(param == 305):
			self.change_Direct3D_settings("RenderTargetModeLock")
		if(param == 306):
			self.change_Direct3D_settings("Multisampling")
		if(param == 307):
			self.change_Direct3D_settings("StrictDrawOrdering")
		if(param == 401):
			self.change_DirectInput_settings("MouseWarpOverride")
		
	
	def AddDisplayElement(self, title, shortname, elements, wine, num):
		elements.insert(0,"Default")
		wine.insert(0,"default")
		self.display_elements[shortname+"_text"] = wx.StaticText(self.panelDisplay, -1, title,pos=(15,19+num*40))
		
		self.display_elements[shortname] = wx.ComboBox(self.panelDisplay, 300+num, style=wx.CB_READONLY,pos=(300,15+num*40))
		self.display_elements[shortname].AppendItems(wine)
		self.display_elements[shortname].SetValue(wine[0])
		wx.EVT_COMBOBOX(self, 300+num,  self.change_settings)
	
				
	def AddMiscElement(self, title, shortname, elements, wine, num):
		elements.insert(0,"Default")
		wine.insert(0,"default")
		self.display_elements[shortname+"_text"] = wx.StaticText(self.panelMisc, -1, title,pos=(15,19+num*40))

		self.display_elements[shortname] = wx.ComboBox(self.panelMisc, 400+num, style=wx.CB_READONLY,pos=(300,15+num*40))
		self.display_elements[shortname].AppendItems(wine)
		self.display_elements[shortname].SetValue(wine[0])
		wx.EVT_COMBOBOX(self, 400+num,  self.change_settings)

		
	def Display(self, nom):
		self.display_elements = {}
		self.panelDisplay = wx.Panel(self, -1)
		
		self.txtDisplay = wx.StaticText(self.panelDisplay, -1, _(nom), (10,10), wx.DefaultSize)
		self.txtDisplay.SetFont(self.fontTitle)
		
		self.AddPage(self.panelDisplay, nom)
		self.AddDisplayElement(_("GSLS Support"),"UseGLSL",["Enabled","Disabled"],["enabled","disabled"],1)
		self.AddDisplayElement(_("Direct Draw Renderer"),"DirectDrawRenderer",["GDI","OpenGL"],["gdi","opengl"],2)
		self.AddDisplayElement(_("Video memory size"),"VideoMemorySize",["32","64","128","256","384","512","768","1024","2048","3072","4096"],["32","64","128","256","384","512","768","1024","2048","3072","4096"],3)
		self.AddDisplayElement(_("Offscreen rendering mode"),"OffscreenRenderingMode",["fbo","backbuffer","pbuffer"],["fbo","backbuffer","pbuffer"],4)
		self.AddDisplayElement(_("Render target mode lock"),"RenderTargetModeLock",["disabeld","readdraw","readtex"],["disabled","readdraw","readtex"],5)
		self.AddDisplayElement(_("Multisampling"),"Multisampling",["Enabled","Disabled"],["enabled","disabled"],6)
		self.AddDisplayElement(_("Strict Draw Ordering"),"StrictDrawOrdering",["enabled","disabled"],["enabled","disabled"],7)

		
	def Miscellaneous(self, nom):
		self.misc_elements = {}
		self.panelMisc = wx.Panel(self, -1)
		
		self.txtMisc = wx.StaticText(self.panelMisc, -1, _(nom), (10,10), wx.DefaultSize)
		self.txtMisc.SetFont(self.fontTitle)
		
		self.AddMiscElement(_("Mouse warp override"),"MouseWarpOverride",["Enabled","Disabled","Force"],["enable","disable","force"],1)
		self.AddPage(self.panelMisc, nom)
		
	def assign(self, event):
		version = self.general_elements["wineversion"].GetValue()
		wine_versions.SetWineVersion(self.s_title, version)
	
	def setname(self, event):
		new_name = self.general_elements["name"].GetValue()
		if(not os.path.exists(Variables.playonlinux_rep+"configurations/installed/"+new_name)):
			try:
				os.rename(Variables.playonlinux_rep+"icones/32/"+self.s_title,Variables.playonlinux_rep+"icones/32/"+new_name)
			except:
				pass
				
				
			try:
				os.rename(Variables.playonlinux_rep+"icones/full_size/"+self.s_title,Variables.playonlinux_rep+"icones/full_size/"+new_name)		
			except: 
				pass
			
			try:
				os.rename(Variables.playonlinux_rep+"configurations/configurators/"+self.s_title,Variables.playonlinux_rep+"configurations/configurators/"+new_name)
			except:
				pass				
		
			try:
					os.rename(Variables.playonlinux_rep+"configurations/installed/"+self.s_title,Variables.playonlinux_rep+"configurations/installed/"+new_name)
					self.s_title = new_name
			except:
				pass
			
			
				
			if(self.changing == False):
				self.Parent.Parent.list_software()
			else:
				self.changing = False

	
class MainWindow(wx.Frame):
	def __init__(self,parent,id,title,shortcut):
		wx.Frame.__init__(self, parent, -1, title, size = (700, 650), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
		self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
		self.panelFenp = wx.Panel(self, -1)
		self.sizer = wx.BoxSizer()   
		
		self.onglets = Onglets(self.panelFenp, shortcut)
		
		self.images = wx.ImageList(16, 16)
		
		if(os.environ["POL_OS"] == "Mac"):
			self.panel_size = (220,650)
		else:
			self.panel_size = wx.DefaultSize
			
		self.list_game = wx.TreeCtrl(self.panelFenp, 900, size = self.panel_size, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)	
		self.list_game.SetSpacing(0);
		self.list_game.SetImageList(self.images)
	
		self.sizer.Add(self.list_game, 1, wx.EXPAND, 0)

		if(shortcut != ""):
			self.sizer.Add(self.onglets, 3, wx.EXPAND, 0)
			self.no_config_yet = False
		else:
			self.no_config_yet = True
			
		self.sizer.Layout()
		self.onglets.General(_("General"))
		self.onglets.Packages(_("Install packages"))
		self.onglets.Display(_("Display"))
		self.onglets.Miscellaneous(_("Miscellaneous"))
		
		self.panelFenp.SetSizer(self.sizer)
		self.panelFenp.SetAutoLayout(True)
		self.list_software()
		wx.EVT_BUTTON(self, wx.ID_APPLY, self.apply_settings)
		wx.EVT_BUTTON(self, wx.ID_CLOSE, self.app_Close)
		wx.EVT_TREE_SEL_CHANGED(self, 900, self.change_program_to_selection)
		self.change_program(shortcut)
		
	def change_program_to_selection(self, event):
		self.change_program(self.list_game.GetItemText(self.list_game.GetSelection()))
		
	def change_program(self, new_prgm):
		if(self.no_config_yet == True):
			self.sizer.Add(self.onglets, 12, wx.EXPAND, 0)
			self.no_config_yet = False
			
		self.new_program = new_prgm
		self.SetTitle(self.new_program+_(" configuration"))
		self.onglets.ChangeTitle(self.new_program)
		self.onglets.general_elements["wineversion"].SetValue(wine_versions.GetWineVersion(self.new_program))
		self.onglets.UpdateValues()
	
	def list_software(self):
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
				self.file_icone = Variables.playonlinux_rep+"/icones/32/"+game
			else:
				self.file_icone = Variables.playonlinux_env+"/etc/playonlinux32.png"

			try:
				self.bitmap = wx.Image(self.file_icone)
				self.bitmap.Rescale(16,16,wx.IMAGE_QUALITY_HIGH)
				self.bitmap = self.bitmap.ConvertToBitmap()
				self.images.Add(self.bitmap)
			except:
				pass
			item = self.list_game.AppendItem(root, game, self.i)
			self.i += 1
	
	def app_Close(self, event):
		self.Destroy()

	def apply_settings(self, event):
		self.Destroy()
