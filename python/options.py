#!/usr/bin/python3
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
import os, subprocess, getopt, sys, urllib.request, signal, socket
import wx, time, re
import webbrowser, shutil
import threading, time, codecs
from select import select

import lib.Variables as Variables
import lib.lng as lng
import lib.playonlinux as playonlinux

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
                    req = urllib.request.Request(url)
                    handle = urllib.request.urlopen(req)
                    time.sleep(1)
                    available_versions = handle.read()
                    available_versions = available_versions.split("\n")
                    self.i = 0
                    self.versions_ = []
                    while(self.i < len(available_versions) - 1):
                        informations = available_versions[self.i].split(";")
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
        self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/extensions.png"));

        self.SetImageList(self.images_onglets)


    def browser_test(self, event):
        if(self.Navigator.GetValue() == "Default"):
            webbrowser.open("http://www.playonlinux.com")
        else:
            subprocess.Popen([self.Navigator.GetValue(), "http://www.playonlinux.com/"])

    def term_test(self, event):
        subprocess.Popen(["bash", Variables.playonlinux_env+"/bash/terminals/"+self.Term.GetValue(), "sleep", "2"])

    def Internet(self, nom):
        self.panelInternet = wx.Panel(self, -1)

        if(os.path.exists(Variables.playonlinux_rep+"/configurations/options/offline")):
            if(open(Variables.playonlinux_rep+"/configurations/options/offline",'r').read() == '1'):
                self.OffLineCheck.SetValue(1)

        self.ProxySettings = wx.StaticText(self.panelInternet, -1, _("Proxy configuration"), (0,0), wx.DefaultSize)
        self.ProxySettings.SetFont(self.fontTitle)

        proxy_settings = {}

        proxy_settings['PROXY_ENABLED'] = playonlinux.GetSettings("PROXY_ENABLED")
        if(proxy_settings['PROXY_ENABLED'] == ""):
            proxy_settings['PROXY_ENABLED'] = "0"
        proxy_settings['PROXY_ADRESS'] = playonlinux.GetSettings("PROXY_URL")
        proxy_settings["PROXY_PORT"] = playonlinux.GetSettings("PROXY_PORT")
        proxy_settings["PROXY_LOGIN"] = playonlinux.GetSettings("PROXY_LOGIN")
        proxy_settings["PROXY_PASS"] = playonlinux.GetSettings("PROXY_PASSWORD")

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
        self.Bind(wx.EVT_CHECKBOX, self.proxy_enable, id=120)
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
        self.pluginlist = wx.TreeCtrl(self.panelPlugins, 220, style=Variables.widget_borders|wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        self.pluginlist.SetSpacing(0)

        self.pluginImgList = wx.ImageList(16,16)

        self.pluginlist.SetImageList(self.pluginImgList)



        self.sizerPlugins.Add(self.txtPlugin, 1, wx.EXPAND|wx.ALL, 2)
        self.sizerPlugins.Add(self.pluginlist, 7, wx.EXPAND|wx.ALL, 2)

        self.sizerPlugins.Add(self.panels_buttons_plugins, 6, wx.EXPAND|wx.ALL, 2)

        self.panelPlugins.SetSizer(self.sizerPlugins)
        self.panelPlugins.SetAutoLayout(True)
        self.AddPlugin = wx.Button(self.panels_buttons_plugins, wx.ID_ADD, _("Add"), pos=(0,0), size=(100,35))
        self.DelPlugin = wx.Button(self.panels_buttons_plugins, wx.ID_REMOVE, _("Remove"), pos=(100,0), size=(100,35))
        self.ConfigurePlugin = wx.Button(self.panels_buttons_plugins, 212, _("Configure"), pos=(0,38), size=(100,35))
        self.EnablePlugin = wx.Button(self.panels_buttons_plugins, 213, _("Enable"), pos=(100,38), size=(100,35))
        self.txtPlugin = wx.StaticText(self.panels_buttons_plugins, -1, _("Choose a plugin"), size=(300,150), pos=(200,5))

        self.LoadPlugins()

        self.AddPage(self.panelPlugins, nom, imageId=5)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.choose_plugin, id=220)

        self.Bind(wx.EVT_BUTTON, self.disable, id=214)
        self.Bind(wx.EVT_BUTTON, self.enable, id=213)
        self.Bind(wx.EVT_BUTTON, self.setup_plug, id=212)
        self.Bind(wx.EVT_BUTTON, self.delete_plug, id=wx.ID_REMOVE)
        self.Bind(wx.EVT_BUTTON, self.add_plug, id=wx.ID_ADD)

    def generateExts(self):
        self.list_ext.DeleteAllItems()
        i = 0
        self.exts = open(os.environ["POL_USER_ROOT"]+"/extensions.cfg").readlines()
        self.exts.sort()
        for line in self.exts:
            line = line.replace("\n","")
            line = line.split("=")
            liner = "Line %s" % i
            self.list_ext.InsertStringItem(i, liner)
            self.list_ext.SetStringItem(i, 0, line[0])
            self.list_ext.SetStringItem(i, 1, line[1])
            i += 1
        self.app_installed_text.Hide()
        self.app_installed.Hide()
        self.delete_ext.Hide()
        self.app_installed.SetValue("")
        self.app_selected = -1

    def reditExt(self, event):

        playonlinux.SetSettings(self.ext_selected, self.app_installed.GetValue(),'_EXT_')
        self.generateExts()

    def editExt(self, event):
        self.app_installed_text.Show()
        self.app_installed.Show()
        self.delete_ext.Show()

        self.app_selected = self.exts[event.m_itemIndex].split("=")[1]
        self.ext_selected = self.exts[event.m_itemIndex].split("=")[0]

        self.app_installed.SetValue(self.app_selected.replace("\n","").replace("\r",""))

    def delExt(self, event):
        playonlinux.DeleteSettings(self.ext_selected,'_EXT_')
        self.generateExts()

    def newExt(self, event):
        newext = wx.GetTextFromUser(_("What is the extension?"), os.environ["APPLICATION_TITLE"])
        re.sub(r'\W+', '', newext)
        playonlinux.SetSettings(newext, "",'_EXT_')

        self.generateExts()

    def Extensions(self, nom):
        self.panelExt= wx.Panel(self, -1)
        self.list_ext = wx.ListCtrl(self.panelExt, 500, size=(504,350), pos=(1,1), style=wx.LC_REPORT)
        self.list_ext.InsertColumn(0, 'Extension')
        self.list_ext.InsertColumn(1, 'Program associated', width=320)

        self.app_installed_text = wx.StaticText(self.panelExt, pos=(1,388), label=_("Assigned program"))
        self.app_installed = wx.ComboBox(self.panelExt, 501, pos=(170,385),size=(200,25))
        self.delete_ext = wx.Button(self.panelExt, 502, pos=(372,385+2*Variables.windows_add_playonmac), size=(100,25), label=_("Delete"))


        self.add_ext = wx.Button(self.panelExt, 503, pos=(1,359), size=(100,25), label=_("New"))


        self.app_installed_list = os.listdir(os.environ["POL_USER_ROOT"]+"/shortcuts/")
        for i in self.app_installed_list:
            self.app_installed.Append(i)

        self.generateExts()
        self.AddPage(self.panelExt, nom, imageId=6)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.editExt, id=500)
        self.Bind(wx.EVT_COMBOBOX, self.reditExt, id=501)
        self.Bind(wx.EVT_BUTTON, self.delExt, id=502)
        self.Bind(wx.EVT_BUTTON, self.newExt, id=503)

    def setup_plug(self, event):
        self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
        self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
        subprocess.Popen(["bash", self.plugin_path+"/scripts/options"])

    def add_plug(self, event):
        self.FileDialog = wx.FileDialog(self)
        self.FileDialog.SetDirectory("~")
        self.FileDialog.SetWildcard("POL Packages (*.pol)|*.pol")
        result = self.FileDialog.ShowModal()
        if(result == wx.ID_OK and self.FileDialog.GetPath() != ""):
            if(wx.YES == wx.MessageBox(_("Are you sure you want to install: ")+self.FileDialog.GetPath()+"?",os.environ["APPLICATION_TITLE"] ,style=wx.YES_NO | wx.ICON_QUESTION)):
                subprocess.call(["bash", Variables.playonlinux_env+"/playonlinux-pkg", "-i", self.FileDialog.GetPath()])
                self.LoadPlugins()
        self.FileDialog.Destroy()

    def delete_plug(self, event):
        self.current_plugin = self.pluginlist.GetItemText(self.pluginlist.GetSelection())
        self.plugin_path = Variables.playonlinux_rep+"/plugins/"+self.current_plugin
        if(wx.YES == wx.MessageBox(_("Are you sure you want to delete: ")+self.current_plugin+"?", os.environ["APPLICATION_TITLE"],style=wx.YES_NO | wx.ICON_QUESTION)):
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
        self.txtGLX.SetValue(subprocess.check_output(["bash", Variables.playonlinux_env+"/bash/system_info"]))

    def SupprimePage(self, index):
        self.DeletePage(index)


class MainWindow(wx.Frame):
    def __init__(self,parent,id,title,onglet):
        wx.Frame.__init__(self, parent, -1, title, size = (505, 550), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX | wx.RESIZE_BORDER)
        self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.panelFenp = wx.Panel(self, -1)
        self.panels_buttons = wx.Panel(self.panelFenp, -1)
        self.Apply = wx.Button(self.panels_buttons, wx.ID_APPLY, _("Apply"), pos=(400,0), size=(100,35))
        self.Close = wx.Button(self.panels_buttons, wx.ID_CLOSE, _("Cancel"), pos=(295,0), size=(100,35))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.onglets = Onglets(self.panelFenp)

        self.sizer.Add(self.onglets, 12, wx.EXPAND|wx.ALL, 2)
        self.sizer.Add(self.panels_buttons, 1, wx.EXPAND|wx.ALL, 2)

        #self.onglets.General(_("General"))
        self.onglets.Internet(_("Internet"))
        #self.onglets.Wine(_("Environment"))
        #self.onglets.System(_("System"))
        self.onglets.Plugins(_("Plugins"))
        self.onglets.Extensions(_("File associations"))

        try:
            self.onglets.SetSelection(onglet)
        except:
            pass

        self.panelFenp.SetSizer(self.sizer)
        self.panelFenp.SetAutoLayout(True)
        self.Bind(wx.EVT_BUTTON, self.apply_settings, id=wx.ID_APPLY)
        self.Bind(wx.EVT_BUTTON, self.app_Close, id=wx.ID_CLOSE)

    def app_Close(self, event):
        self.Destroy()

    def apply_settings(self, event):
        playonlinux.SetSettings("PROXY_ENABLED",str(int(self.onglets.ProxyCheck.IsChecked())))
        if(self.onglets.ProxyCheck.IsChecked()):
            playonlinux.SetSettings("PROXY_URL",self.onglets.ProxyAdresse.GetValue().replace("http://",""))
            playonlinux.SetSettings("PROXY_PORT",self.onglets.ProxyPort.GetValue())
            playonlinux.SetSettings("PROXY_LOGIN",self.onglets.ProxyLogin.GetValue())
            playonlinux.SetSettings("PROXY_PASSWORD",self.onglets.ProxyPass.GetValue())


        wx.MessageBox(_("You must restart {0} for the changes to take effect.").format(os.environ["APPLICATION_TITLE"]), os.environ["APPLICATION_TITLE"], wx.OK)
        self.Destroy()
