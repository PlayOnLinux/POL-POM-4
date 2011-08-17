#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Pâris Quentin

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

# Wrapper.py - Enable running PlayOnLinux and PlayOnMac scripts outside of POL/POM environement

encoding = 'utf-8'

import os, getopt, sys, urllib, signal, string, time, webbrowser, gettext, locale, sys, shutil, subprocess
import wx
	
import lib.Variables as Variables, lib.lng as lng
import guiv3 as gui, install, options, wine_versions as wver, sp, configure, threading

lng.Lang()


polid=os.environ["POL_ID"]

class Program(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()
		
	def run(self):
		self.running = True
		self.chaine = ""
		for arg in sys.argv[2:]:
			self.chaine+=" \""+arg+"\""
		self.proc = subprocess.Popen("bash \""+sys.argv[1]+"\""+self.chaine, shell=True)
		while(self.running == True):
			self.proc.poll()
			time.sleep(1)
		
		
class PlayOnLinuxApp(wx.App):
	def OnInit(self):
		lng.iLang()
		
		
		self.SetClassName(os.environ["APPLICATION_TITLE"])
		self.SetAppName(os.environ["APPLICATION_TITLE"])
		self.frame = gui.POL_SetupFrame(os.environ["APPLICATION_TITLE"],str(pid_to_open),top,left,str(pid_to_open))
		self.frame.Center(wx.BOTH)
		self.frame.Show(True)

		
		return True

prog = Program()
pid_to_open = -1
left = None
top = None
while(True):
	time.sleep(1)
	if(prog.proc.returncode == None):
		fichier_index = os.environ["REPERTOIRE"]+"/configurations/guis/index_"+polid
		fichier_index = os.environ["REPERTOIRE"]+"/configurations/guis/index_"+os.environ["POL_ID"]
		#print(fichier_index)
		try:
			message = open(fichier_index,'r').read()
		except:
			open(fichier_index,'a').write('')
			message = open(fichier_index,'r').read()
		message = string.split(message, "\n")
		if(message[0] == "Open"):
			pid_to_open = message[1]
			top = message[2]
			left = message[3]
			app = PlayOnLinuxApp(redirect=False)
			app.MainLoop()
	else:
		prog.running = False
		os._exit(0)
	#time.sleep(1)		
