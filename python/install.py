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

import wx
import os, sys, codecs, string, socket, urllib, urllib2
import wx.html, threading, time, wx.animate

import lib.Variables as Variables, sp
import lib.lng

class getDescription(threading.Thread):
  def __init__(self):
	threading.Thread.__init__(self)
	self.getDescription = ""
	self.getDescription_bis = ""
	self.htmlContent = ""
	self.htmlwait = "###WAIT###"
	self.stars = 0
	self.cat = 0
	self.start()
	self.miniature = Variables.playonlinux_env+"/resources/images/pol_min.png"
	self.miniature_defaut = Variables.playonlinux_env+"/resources/images/pol_min.png"
	
  def download(self, game):
	self.getDescription = game
	
	
  def run(self):
	self.thread_running = True
	while(self.thread_running):
		if(self.getDescription == ""):
			time.sleep(0.1)
		else:
			self.htmlContent = self.htmlwait;
			time.sleep(0.5)
			self.getDescription_bis = self.getDescription
			
			if(self.getDescription == "about:conceptor"):
				self.miniature = self.miniature_defaut
				self.htmlContent = "Well done !"
				self.stars = "5"
			else:
				
				self.cut = string.split(self.getDescription,":")
				if(self.cut[0] == "get"):
					self.miniature = self.miniature_defaut
					# Description
				   	self.htmlContent = "<font color=red><b>WARNING !</b><br />You are going to execute a non-validated script. <br />This functionality has been added to make script testing easier.<br />It can be dangerous for your computer. <br />PlayOnLinux will NOT be reponsible for any damages.</font>"
					self.stars = "0"
				else:
					# Miniatures
					try :
						url = os.environ["SITE"]+'/V2_data/miniatures/'+self.getDescription.replace(" ","%20")
						req = urllib2.Request(url)
						handle = urllib2.urlopen(req)
						open(Variables.playonlinux_rep+"/tmp/min","w").write(handle.read())
						self.miniature = Variables.playonlinux_rep+"/tmp/min"
					except :
						self.miniature = self.miniature_defaut

					# Description
					try :
						url = os.environ["SITE"]+'/V3_data/repository/get_description.php?id='+self.getDescription.replace(" ","%20")
						req = urllib2.Request(url)
						handle = urllib2.urlopen(req)
						self.htmlContent = handle.read()
					except :
						self.htmlContent = "<i>"+_("No description")+"</i>"

					if(self.cat == 12):
						self.htmlContent += "<br /><br /><font color=red><b>WARNING !</b><br />You are going to execute a beta script. <br />This functionality has been added to make script testing easier.<br />It might not work as expected.</font>"

					# Stars
					try :
						url = os.environ["SITE"]+'/V3_data/repository/stars.php?n='+self.getDescription.replace(" ","%20")
						req = urllib2.Request(url)
						handle = urllib2.urlopen(req)
						self.stars = handle.read()
					except :
						self.stars = "0"
			
				
			if(self.getDescription == self.getDescription_bis):
				self.getDescription = ""


class InstallWindow(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self, parent, -1, title, size = (792, 580+Variables.windows_add_size), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
		self.description = getDescription()
		self.panelFenp = wx.Panel(self, -1)
		self.live = 0
		self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
		self.images_cat = wx.ImageList(22, 22)
		self.imagesapps = wx.ImageList(22, 22)
		self.list_cat = wx.TreeCtrl(self.panelFenp, 105, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|Variables.widget_borders, size=(200, 363), pos=(10,10))
		if(os.environ["POL_OS"] == "Mac"):
			self.image_position = (8,381)
			self.new_size = (558,218)
		if(os.environ["POL_OS"] == "Linux"):
			self.image_position = (10,383)
			self.new_size = (562,222)
		
		self.image = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(Variables.playonlinux_env+"/resources/images/pol_min.png"), self.image_position, wx.DefaultSize)
		self.list_cat.SetSpacing(0);
		self.list_cat.SetImageList(self.images_cat)
		self.AddCats()
		self.searchbox = wx.TextCtrl(self.panelFenp, 110, size=(364,20), pos=(319,9))
		self.searchcaption = wx.StaticText(self.panelFenp, -1, _("Search: "), (220,12), wx.DefaultSize)
		self.lasthtml_content = ""
		self.list_apps = wx.TreeCtrl(self.panelFenp, 106, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|Variables.widget_borders, size=(562, 266), pos=(220,35))
		self.list_apps.SetImageList(self.imagesapps)
		self.list_apps.SetSpacing(0);
		self.stars = 0
		#self.content =  wx.TextCtrl(self.panelFenp, 107, pos=(220,301), size=(562,212), style = wx.TE_MULTILINE | wx.TE_RICH2 | wx.CB_READONLY | Variables.widget_borders)
		self.content = wx.html.HtmlWindow(self.panelFenp, 107, style=Variables.widget_borders, pos=(220,311), size=(562,222))
		self.button = wx.Button(self.panelFenp, wx.ID_CLOSE, _("Cancel"), pos=(576, 540), size=(100,35))
		self.install_button = wx.Button(self.panelFenp, wx.ID_APPLY, _("Install"), pos=(683, 540), size=(100,35))
		#self.update_button = wx.Button(self.panelFenp, wx.ID_REFRESH, _("Refresh"), pos=(470, 540), size=(100,35))
		self.install_button.Enable(False)
		
		self.new_panel = wx.Panel(self.panelFenp, -1, pos=(220,311), style=Variables.widget_borders, size=self.new_size)
		self.new_panel.SetBackgroundColour((255,255,255))
		self.animation = wx.animate.GIFAnimationCtrl(self.new_panel, -1, Variables.playonlinux_env+"/etc/24-0.gif", (271,96))

		self.new_panel.Hide()

		self.timer = wx.Timer(self, 1)
		self.Bind(wx.EVT_TIMER, self.TimerAction, self.timer)
		self.timer.Start(200)

		#self.ManualInstall = wx.CheckBox(self.panelFenp, 111, label=_("Install a .pol package or an unsupported application"), pos=(10,530))
		self.ManualInstall = wx.HyperlinkCtrl(self.panelFenp, 111, _("Install a non-listed program"), "", pos=(10,545))
		self.ManualInstall.SetNormalColour(wx.Colour(0,0,0))
   # self.AddApps()

		wx.EVT_TREE_SEL_CHANGED(self, 105, self.AddApps)
		wx.EVT_TREE_SEL_CHANGED(self, 106, self.AppsDetails)
		wx.EVT_BUTTON(self, wx.ID_CLOSE, self.closeapp)
		wx.EVT_BUTTON(self, wx.ID_APPLY, self.installapp)
		#wx.EVT_BUTTON(self, wx.ID_REFRESH, self.UpdatePol)
		wx.EVT_CLOSE(self, self.closeapp)
		wx.EVT_TREE_ITEM_ACTIVATED(self, 106, self.installapp)
		wx.EVT_TEXT(self, 110, self.search)
		wx.EVT_HYPERLINK(self, 111, self.manual)
		#wx.EVT_CHECKBOX(self, 111, self.manual)
		#Timer, regarde toute les secondes si il faut actualiser la liste

	def TimerAction(self, event):
		if(self.lasthtml_content != self.description.htmlContent):
			self.SetImg(self.description.miniature)
			self.description.miniature = self.description.miniature_defaut
			self.lasthtml_content = self.description.htmlContent;
			if(self.description.htmlContent == "###WAIT###"):
				self.content.Hide()
				self.animation.Show()
				self.animation.Play()
				self.new_panel.Show()
				self.Refresh()
			else:
				self.animation.Hide()
				self.animation.Stop()
				self.new_panel.Hide()
				self.content.Show()
				self.Refresh()
				self.content.SetPage(self.description.htmlContent)
	

		if(self.stars != self.description.stars):
			self.show_stars(self.description.stars)
			self.stars = self.description.stars
		
		if(self.list_cat.GetItemImage(self.list_cat.GetSelection()) != self.description.cat):
			self.description.cat = self.list_cat.GetItemImage(self.list_cat.GetSelection())

	def closeapp(self, event):
		self.description.thread_running = False	
		self.Destroy()  

	def manual(self, event):
		self.live = 1
		self.installapp(self)

	def show_stars(self, stars):
		self.stars = int(stars)
		
		try :
			self.star1.Destroy()
		except :
			pass
		try :
			self.star2.Destroy()
		except :
			pass
		try :
			self.star3.Destroy()
		except :
			pass
		try :
			self.star4.Destroy()
		except :
			pass
		try :
			self.star5.Destroy()
		except :
			pass

		self.stars = int(self.stars)

		if(self.stars == 5):
			self.star5 = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(Variables.playonlinux_env+"/etc/star.png"), (762,12), wx.DefaultSize)
		if(self.stars >= 4):
			self.star4 = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(Variables.playonlinux_env+"/etc/star.png"), (744,12), wx.DefaultSize)
		if(self.stars >= 3):
			self.star3 = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(Variables.playonlinux_env+"/etc/star.png"), (726,12), wx.DefaultSize)
		if(self.stars >= 2):
			self.star2 = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(Variables.playonlinux_env+"/etc/star.png"), (708,12), wx.DefaultSize)
		if(self.stars >= 1):
			self.star1 = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(Variables.playonlinux_env+"/etc/star.png"), (690,12), wx.DefaultSize)

	def UpdatePol(self, event):
		self.DelApps()
		os.system("bash \""+Variables.playonlinux_env+"/bash/check_maj\"&")
	
	def installapp(self, event):
		if(self.live == 1):
			InstallApplication = "ExecLiveInstall"
		else:
			InstallApplication = self.list_apps.GetItemText(self.list_apps.GetSelection())
	
		if(InstallApplication == "about:conceptor"):
			self.EasterEgg = sp.egg(None, -1, "PlayOnLinux Conceptor")
			self.EasterEgg.Show()
			self.EasterEgg.Center(wx.BOTH)
		else:
			os.system("bash \""+Variables.playonlinux_env+"/bash/install\" \""+InstallApplication+"\"&")
	
		self.Destroy()
		return  

	def search(self, event):
		self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/search",'r',"utf-8")
		self.apps = self.apps.readlines()
		self.j = 0;
		while(self.j < len(self.apps)):
			self.apps[self.j] = self.apps[self.j].replace("\n","")
			self.j += 1
			
		self.j = 0;
		self.k = 0;
		self.user_search =self.searchbox.GetValue()
		self.search_result = []

		while(self.j < len(self.apps)):
			if(string.lower(self.user_search) in string.lower(self.apps[self.j])):
				self.search_result.append(self.apps[self.j])
				self.k = self.k + 1;
			self.j = self.j + 1;

		if(self.user_search == "about:conceptor"):
			self.search_result.append("about:conceptor")

		self.user_search_cut = string.split(self.user_search,":")
		if(len(self.user_search_cut) > 1):
			if(self.user_search_cut[0] == "get" and self.user_search_cut[1].isdigit()):
				self.search_result.append(self.user_search)
				
		if(self.user_search != ""):
			self.WriteApps(self.search_result)
		else:
			self.DelApps()


	def EraseDetails(self):
		self.content.SetValue("");

	def AppsDetails(self, event):
		self.install_button.Enable(True)
		self.application = self.list_apps.GetItemText(self.list_apps.GetSelection())
		self.description.download(self.application)

	def AddCats(self):
		self.cats = [_("Accessories"),_("Development"),_("Education"),_("Games"),_("Graphics"),_("Internet"),_("Multimedia"),_("Office"),_("Other")]
		self.images_cat.RemoveAll()
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-accessories.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-development.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/edu.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-games.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-graphics.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-internet.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-multimedia.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-office.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-other.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/emblem-favorite.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/face-smile.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/view-refresh.png"))
		self.images_cat.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/applications-testing.png"))
	
		self.list_cat.DeleteAllItems()
		self.root = self.list_cat.AddRoot("")
		self.i = 0
		for cat in self.cats:
			self.list_cat.AppendItem(self.root, cat, self.i)
			self.i = self.i+1

		self.list_cat.AppendItem(self.root, "",-1)
		self.list_cat.AppendItem(self.root, _("Highest rated"), self.i)
		self.list_cat.AppendItem(self.root, _("Most downloaded"), self.i+1)
		self.list_cat.AppendItem(self.root, _("Patches"), self.i+2)
		self.list_cat.AppendItem(self.root, _("Testing"), self.i+3)

	def WriteApps(self, array):
		self.imagesapps.RemoveAll()

		self.DelApps()
		self.root_apps = self.list_apps.AddRoot("")
		self.i = 0
		array.sort()
		for app in array:
			self.icon_look_for = Variables.playonlinux_rep+"/configurations/icones/"+app
			if(os.path.exists(self.icon_look_for)):
				try:
					self.imagesapps.Add(wx.Bitmap(self.icon_look_for))
				except:
					pass
			else:	
				self.imagesapps.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/playonlinux22.png"))
			self.list_apps.AppendItem(self.root_apps, app, self.i)
			self.i = self.i+1

	def DelApps(self):
		self.list_apps.DeleteAllItems()

	def SetImg(self, image):
		self.image.Destroy()
		self.image = wx.StaticBitmap(self.panelFenp, -1, wx.Bitmap(image), self.image_position, wx.DefaultSize)
		self.Refresh()

	def ResetImg(self):
		self.SetImg(Variables.playonlinux_env+"/resources/images/pol_min.png")

	def AddApps(self, event):
		self.searchbox.SetValue("")
		#self.cat_selected=self.list_cat.GetItemText(self.list_cat.GetSelection()).encode('utf-8')
		self.cat_selected = self.list_cat.GetItemImage(self.list_cat.GetSelection())
		#print self.cat_selected
		if(self.cat_selected == 8):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/0",'r',"utf-8")
		if(self.cat_selected == 3):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/1",'r',"utf-8")
		if(self.cat_selected == 0):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/2",'r',"utf-8")
		if(self.cat_selected == 7):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/3",'r',"utf-8")
		if(self.cat_selected == 5):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/4",'r',"utf-8")
		if(self.cat_selected == 6):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/5",'r',"utf-8")
		if(self.cat_selected == 4):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/6",'r',"utf-8")
		if(self.cat_selected == 1):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/7",'r',"utf-8")
		if(self.cat_selected == 2):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/8",'r',"utf-8")
		if(self.cat_selected == 11):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/9",'r',"utf-8")
		if(self.cat_selected == 12):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/10",'r',"utf-8")
		if(self.cat_selected == 10):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/download",'r',"utf-8")
		if(self.cat_selected == 9):
			self.apps = codecs.open(Variables.playonlinux_rep+"/configurations/listes/rate",'r',"utf-8")

		self.apps = self.apps.readlines()
		self.j = 0
		while(self.j < len(self.apps)):
			self.apps[self.j] = self.apps[self.j].replace("\n","")
			self.j += 1
		self.WriteApps(self.apps)
