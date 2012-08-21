#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007 Pâris Quentin
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

import wxversion, os, getopt, sys, urllib, signal, socket, codecs, string, shutil, time, urllib, urllib2
import wx, wx.animate

import lib.Variables as Variables
import lib.lng, threading

if(os.environ["POL_OS"] == "Mac"):
    os_pref = "darwin"
else:
    os_pref = "linux"

lib.lng.Lang()

def SetWineVersion(game, version):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    fichier = open(cfile,"r").readlines()
    i = 0
    line = []
    while(i < len(fichier)): # On retire l'eventuel
        fichier[i] = fichier[i].replace("\n","")
        if("PATH=" not in fichier[i] or "WineVersions" not in fichier[i]):
            line.append(fichier[i])
        i += 1

    fichier_write = open(cfile,"w")

    if(version != "System"): # On insere
        if(os.environ["POL_OS"] == "Mac"):
            line.insert(1,"PATH=\""+Variables.playonlinux_rep+"WineVersions/"+version+"/bin/:$PATH\"")
            line.insert(1,"LD_LIBRARY_PATH=\""+Variables.playonlinux_rep+"WineVersions/"+version+"/lib/:$LD_LIBRARY_PATH\"")
        else:
            line.insert(1,"PATH=\""+Variables.playonlinux_rep+"WineVersions/"+version+"/usr/bin/:$PATH\"")
            line.insert(1,"LD_LIBRARY_PATH=\""+Variables.playonlinux_rep+"WineVersions/"+version+"/usr/lib/:$LD_LIBRARY_PATH\"")


    i = 0
    while(i < len(line)): # On ecrit
        fichier_write.write(line[i]+"\n")
        i+=1

def GetWineVersion(game):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    fichier = open(cfile,"r").readlines()
    i = 0
    line = ""
    while(i < len(fichier)):
        fichier[i] = fichier[i].replace("\n","")
        if("PATH=" in fichier[i] and "WineVersions" in fichier[i]):
            line = fichier[i].replace("//","/")
        i += 1

    if(line == ""):
        version = "System"
    else:
        version=line.replace("PATH=","").replace("\"","").replace(Variables.playonlinux_rep,"").replace("//","/")
        version = string.split(version,"/")
        version = version[1]

    return(version)


def keynat(string):
    r'''A natural sort helper function for sort() and sorted()
    without using regular expressions or exceptions.

    >>> items = ('Z', 'a', '10th', '1st', '9')
    >>> sorted(items)
    ['10th', '1st', '9', 'Z', 'a']
    >>> sorted(items, key=keynat)
    ['1st', '9', '10th', 'a', 'Z']

    Borrowed from http://code.activestate.com/recipes/285264/#c6
    by paul clinch.

    License is the PSF Python License, http://www.python.org/psf/license/ (GPL compatible)
    '''
    it = type(1)
    r = []
    for c in string:
        if c.isdigit():
            d = int(c)
            if r and type( r[-1] ) == it:
                r[-1] = r[-1] * 10 + d
            else:
                r.append(d)
        else:
            r.append(c.lower())
    return r

class getVersions(threading.Thread):
    def __init__(self, arch="x86"):
        threading.Thread.__init__(self)
        self.thread_message = "#WAIT#"
        self.versions = []
        self.architecture = arch
        self.start()

    def download(self, game):
        self.getDescription = game

    def run(self):
        self.thread_running = True
        while(self.thread_running):
            if(self.thread_message == "get"):
                wfolder = os_pref+"-"+self.architecture
                try :

                    url = os.environ["WINE_SITE"]+"/"+wfolder+".lst"

                    #print(url)
                    req = urllib2.Request(url)
                    handle = urllib2.urlopen(req, timeout = 2)
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
                        if(not os.path.exists(Variables.playonlinux_rep+"/wine/"+wfolder+"/"+version)):
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
        self.notebook = wx.Notebook.__init__(self, parent, -1)
        self.images_onglets = wx.ImageList(16, 16)
        self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/wine.png"))
        self.SetImageList(self.images_onglets)
        self.panelFenp = {}
        self.imagesapps = {}
        self.imagesapps_i = {}
        self.list_apps = {}
        self.new_panel = {}
        self.list_ver_installed = {}
        self.button_rm = {}
        self.button_in = {}

    def liste_versions(self, arch="x86"):
        if(arch == "amd64"):
            add=100
        else:
            add=0
        self.panelFenp[arch] = wx.Panel(self, -1)
        self.imagesapps[arch] = wx.ImageList(22, 22)
        self.imagesapps_i[arch] = wx.ImageList(22, 22)


        self.list_apps[arch] = wx.TreeCtrl(self.panelFenp[arch], 106+add, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|Variables.widget_borders, size=(320, 300), pos=(10,35))
        self.list_apps[arch].SetImageList(self.imagesapps[arch])
        self.list_apps[arch].SetSpacing(0);

        self.new_panel[arch] = wx.Panel(self.panelFenp[arch], -1, pos=(10,505), size=(100,100))

        self.list_ver_installed[arch] = wx.TreeCtrl(self.panelFenp[arch], 107+add, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|Variables.widget_borders, size=(320, 300), pos=(400,35))
        self.list_ver_installed[arch].SetImageList(self.imagesapps_i[arch])
        self.list_ver_installed[arch].SetSpacing(0);
        wx.StaticText(self.panelFenp[arch], -1, _("Installed Wine versions: "),(395,10))
        wx.StaticText(self.panelFenp[arch], -1, _("Available Wine versions: "),(5,10))

        self.button_rm[arch] = wx.Button(self.panelFenp[arch], 108+add, "<", pos=(340, 175), size=(50,30))
        self.button_in[arch] = wx.Button(self.panelFenp[arch], 109+add,">", pos=(340, 125), size=(50,30))

        self.button_rm[arch].Enable(False)
        self.button_in[arch].Enable(False)
        self.AddPage(self.panelFenp[arch], _("Wine versions")+" ("+arch+")", imageId=0)






class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        self.download32 = getVersions("x86")
        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            self.download64 = getVersions("amd64")

        wx.Frame.__init__(self, parent, -1, title, size = (750, 400+Variables.windows_add_size), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
        self.timer = wx.Timer(self, 1)
        self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        #self.panel = wx.Panel(self, -1)

        self.onglets = Onglets(self)
        #self.sizer = wx.BoxSizer(wx.VERTICAL)
        #self.sizer.Add(self.onglets, 15, wx.EXPAND|wx.ALL, 2)

        self.getVersions("x86")
        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            self.getVersions("amd64")
        #self.panel.SetSizer(self.sizer)
        #self.panel.SetAutoLayout(True)

        self.onglets.liste_versions()
        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            self.onglets.liste_versions("amd64")
        self.oldreload32=""

        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            self.oldreload64=""

        self.oldversions32 = []

        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            self.oldversions64 = []

        #self.button = wx.Button(self.panels_buttons, wx.ID_CLOSE, _("Close"), pos=(510, 5), size=wx.DefaultSize)

        wx.EVT_BUTTON(self, wx.ID_CLOSE, self.closeapp)
        wx.EVT_CLOSE(self, self.closeapp)
        wx.EVT_TREE_SEL_CHANGED(self, 106, self.unselect32)
        wx.EVT_TREE_SEL_CHANGED(self, 107, self.unselect32)
        wx.EVT_BUTTON(self, 108, self.delete32)
        wx.EVT_BUTTON(self, 109, self.install32)

        wx.EVT_TREE_SEL_CHANGED(self, 206, self.unselect64)
        wx.EVT_TREE_SEL_CHANGED(self, 207, self.unselect64)
        wx.EVT_BUTTON(self, 208, self.delete64)
        wx.EVT_BUTTON(self, 209, self.install64)

        self.Bind(wx.EVT_TIMER, self.AutoReload, self.timer)
        self.timer.Start(200)

    def AutoReload(self, event):
        reload32 = os.listdir(Variables.playonlinux_rep+"/wine/"+os_pref+"-x86")
        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            reload64 = os.listdir(Variables.playonlinux_rep+"/wine/"+os_pref+"-amd64")
        if(self.download32.thread_message == "Ok" or self.download32.thread_message == "Err"):
            self.onglets.new_panel["x86"].Hide()
            self.WriteVersion()
            self.download32.thread_message = "Wait"

        else:
            if(self.download32.thread_message != "Wait"):
                self.onglets.new_panel["x86"].Show()


        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            if(self.download64.thread_message == "Ok" or self.download64.thread_message == "Err"):
                self.onglets.new_panel["amd64"].Hide()
                self.WriteVersion("amd64")
                self.download64.thread_message = "Wait"
            else:
                if(self.download64.thread_message != "Wait"):
                    self.onglets.new_panel["amd64"].Show()

        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            if(reload64 != self.oldreload64):
                self.getVersions("amd64")
                self.oldreload64 = reload64

        if(reload32 != self.oldreload32):
            self.getVersions()
            self.oldreload32 = reload32

        if(self.download32.versions != self.oldversions32):
            self.oldversions32 = self.download32.versions[:]

        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            if(self.download64.versions != self.oldversions64):
                self.oldversions64 = self.download64.versions[:]



    def sizedirectory(self, path):
        size = 0
        for root, dirs, files in os.walk(path):
            for fic in files:
                size += os.path.getsize(os.path.join(root, fic))
        return size

    def unselect32(self, event):
        if(event.GetId() == 106):
            self.onglets.list_ver_installed["x86"].UnselectAll()
            self.onglets.button_rm["x86"].Enable(False)
            self.onglets.button_in["x86"].Enable(True)
        if(event.GetId() == 107):
            self.onglets.list_apps["x86"].UnselectAll()
            self.onglets.button_rm["x86"].Enable(True)
            self.onglets.button_in["x86"].Enable(False)

    def delete32(self, event):
        version = self.onglets.list_ver_installed["x86"].GetItemText(self.onglets.list_ver_installed["x86"].GetSelection()).encode("utf-8","replace")

        if(wx.YES == wx.MessageBox(_('Are you sure you want to delete wine {0}?').format(version).decode("utf-8","replace"), os.environ["APPLICATION_TITLE"],style=wx.YES_NO | wx.ICON_QUESTION)):
            shutil.rmtree(Variables.playonlinux_rep+"/wine/"+os_pref+"-x86/"+version)

    def install32(self, event):
        install = self.onglets.list_apps["x86"].GetItemText(self.onglets.list_apps["x86"].GetSelection()).encode("utf-8","replace")
        os.system("bash \""+Variables.playonlinux_env+"/bash/install_wver\" "+install+" x86 &")


    def unselect64(self, event):
        if(event.GetId() == 206):
            self.onglets.list_ver_installed["amd64"].UnselectAll()
            self.onglets.button_rm["amd64"].Enable(False)
            self.onglets.button_in["amd64"].Enable(True)
        if(event.GetId() == 207):
            self.onglets.list_apps["amd64"].UnselectAll()
            self.onglets.button_rm["amd64"].Enable(True)
            self.onglets.button_in["amd64"].Enable(False)

    def delete64(self, event):
        version = self.onglets.list_ver_installed["amd64"].GetItemText(self.onglets.list_ver_installed["amd64"].GetSelection()).encode("utf-8","replace")
        if(wx.YES == wx.MessageBox("Are you sure you want to delete wine "+version+"?", style=wx.YES_NO | wx.ICON_QUESTION)):
            shutil.rmtree(Variables.playonlinux_rep+"/wine/"+os_pref+"-amd64/"+version)

    def install64(self, event):
        install = self.onglets.list_apps["amd64"].GetItemText(self.onglets.list_apps["amd64"].GetSelection()).encode("utf-8","replace")
        os.system("bash \""+Variables.playonlinux_env+"/bash/install_wver\" "+install+" amd64 &")

    def getVersions(self, arch="x86"):
        if(arch == "x86"):
            self.download32.thread_message = "get"
        if(arch == "amd64"):
            self.download64.thread_message = "get"


    def WriteVersion(self, arch="x86"):
        self.onglets.imagesapps[arch].RemoveAll()
        self.onglets.imagesapps_i[arch].RemoveAll()
        self.onglets.list_apps[arch].DeleteAllItems()
        self.onglets.list_ver_installed[arch].DeleteAllItems()

        root = self.onglets.list_apps[arch].AddRoot("")
        self.i = 0
        if(arch == "x86"):
            while(self.i < len(self.download32.versions)):
                self.onglets.imagesapps[arch].Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/wine-packages.png"))
                self.onglets.list_apps[arch].AppendItem(root,self.download32.versions[self.i],self.i)
                self.i += 1
        if(arch == "amd64"):
            while(self.i < len(self.download64.versions)):
                self.onglets.imagesapps[arch].Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/wine-packages.png"))
                self.onglets.list_apps[arch].AppendItem(root,self.download64.versions[self.i],self.i)
                self.i += 1

        root2 = self.onglets.list_ver_installed[arch].AddRoot("")
        wfolder = os_pref+"-"+arch

        installed_versions = os.listdir(Variables.playonlinux_rep+"/wine/"+wfolder)
        installed_versions.sort(key=keynat)
        installed_versions.reverse()
        self.i = 0
        self.j = 0
        while(self.i < len(installed_versions)):
            if(os.path.isdir(Variables.playonlinux_rep+"/wine/"+wfolder+"/"+installed_versions[self.i])):
                if(len(os.listdir(Variables.playonlinux_rep+"/wine/"+wfolder+"/"+installed_versions[self.i])) == 0):
                    self.onglets.imagesapps_i[arch].Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/wine-warning.png"))
                else:
                    self.onglets.imagesapps_i[arch].Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/wine.png"))
                self.onglets.list_ver_installed[arch].AppendItem(root2,installed_versions[self.i],self.j)
                self.j += 1
            self.i += 1
        try :
            if(versions[0] == "Wine packages website is unavailable"):
                self.onglets.list_apps[arch].Enable(False)
                self.onglets.imagesapps[arch].RemoveAll()
        except :
            pass
        self.onglets.button_rm[arch].Enable(False)
        self.onglets.button_in[arch].Enable(False)

    def closeapp(self, event):
        self.download32.thread_running = False
        if(os.environ["AMD64_COMPATIBLE"] == "True"):
            self.download64.thread_running = False

        self.Destroy()
