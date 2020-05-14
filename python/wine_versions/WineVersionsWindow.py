#!/usr/bin/python3
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

import os
import shutil
import subprocess

import wx
import natsort

import lib.Variables as Variables
import lib.lng
import lib.playonlinux as playonlinux
from wine_versions.WineVersionsFetcher import WineVersionFetcher
from wine_versions.WineVersionsNotebook import WineVersionsNotebook
from wine_versions.WineVersionsTools import fetchUserOS

lib.lng.Lang()


def SetWineVersion(game, version):
    cfile = Variables.playonlinux_rep + "shortcuts/" + game
    fichier = open(cfile, "r").readlines()
    i = 0
    line = []
    while (i < len(fichier)):  # On retire l'eventuel
        fichier[i] = fichier[i].replace("\n", "")
        if ("PATH=" not in fichier[i] or "WineVersions" not in fichier[i]):
            line.append(fichier[i])
        i += 1

    fichier_write = open(cfile, "w")

    if (version != "System"):  # On insere
        if os.environ["POL_OS"] == "Mac":
            line.insert(1, "PATH=\"" + Variables.playonlinux_rep + "WineVersions/" + version + "/bin/:$PATH\"")
            line.insert(1,
                        "LD_LIBRARY_PATH=\"" + Variables.playonlinux_rep + "WineVersions/" + version + "/lib/:$LD_LIBRARY_PATH\"")
        else:
            line.insert(1, "PATH=\"" + Variables.playonlinux_rep + "WineVersions/" + version + "/usr/bin/:$PATH\"")
            line.insert(1,
                        "LD_LIBRARY_PATH=\"" + Variables.playonlinux_rep + "WineVersions/" + version + "/usr/lib/:$LD_LIBRARY_PATH\"")

    i = 0
    while (i < len(line)):  # On ecrit
        fichier_write.write(line[i] + "\n")
        i += 1





class WineVersionsWindow(wx.Frame):
    def __init__(self, parent, id, title):
        self.download32 = WineVersionFetcher("x86")
        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.download64 = WineVersionFetcher("amd64")

        wx.Frame.__init__(self, parent, -1, title, size=(750, 400 + Variables.windows_add_size),
                          style=wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
        self.timer = wx.Timer(self, 1)
        self.SetIcon(wx.Icon(Variables.playonlinux_env + "/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        # self.panel = wx.Panel(self, -1)

        self.onglets = WineVersionsNotebook(self)
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(self.onglets, 15, wx.EXPAND|wx.ALL, 2)

        self.getVersions("x86")
        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.getVersions("amd64")
        # self.panel.SetSizer(self.sizer)
        # self.panel.SetAutoLayout(True)

        self.onglets.liste_versions()
        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.onglets.liste_versions("amd64")
        self.oldreload32 = ""

        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.oldreload64 = ""

        self.oldversions32 = []

        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.oldversions64 = []

        # self.button = wx.Button(self.panels_buttons, wx.ID_CLOSE, _("Close"), pos=(510, 5), size=wx.DefaultSize)

        self.Bind(wx.EVT_BUTTON, self.closeapp, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_CLOSE, self.closeapp)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.unselect32, id=106)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.unselect32, id=107)
        self.Bind(wx.EVT_BUTTON, self.delete32, id=108)
        self.Bind(wx.EVT_BUTTON, self.install32, id=109)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.unselect64, id=206)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.unselect64, id=207)
        self.Bind(wx.EVT_BUTTON, self.delete64, id=208)
        self.Bind(wx.EVT_BUTTON, self.install64, id=209)

        self.Bind(wx.EVT_TIMER, self.AutoReload, self.timer)
        self.timer.Start(200)

    def AutoReload(self, event):
        reload32 = os.listdir(Variables.playonlinux_rep + "/wine/" + fetchUserOS() + "-x86")
        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            reload64 = os.listdir(Variables.playonlinux_rep + "/wine/" + fetchUserOS() + "-amd64")
        if (self.download32.thread_message == "Ok" or self.download32.thread_message == "Err"):
            self.WriteVersion()
            self.download32.thread_message = "Wait"

        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            if (self.download64.thread_message == "Ok" or self.download64.thread_message == "Err"):
                self.WriteVersion("amd64")
                self.download64.thread_message = "Wait"

        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            if (reload64 != self.oldreload64):
                self.getVersions("amd64")
                self.oldreload64 = reload64

        if (reload32 != self.oldreload32):
            self.getVersions()
            self.oldreload32 = reload32

        if (self.download32.versions != self.oldversions32):
            self.oldversions32 = self.download32.versions[:]

        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            if (self.download64.versions != self.oldversions64):
                self.oldversions64 = self.download64.versions[:]

    def sizedirectory(self, path):
        size = 0
        for root, dirs, files in os.walk(path):
            for fic in files:
                size += os.path.getsize(os.path.join(root, fic))
        return size

    def unselect32(self, event):
        if (event.GetId() == 106):
            self.onglets.installedWineVersionsTreeSelector["x86"].UnselectAll()
            self.onglets.button_rm["x86"].Enable(False)
            self.onglets.button_in["x86"].Enable(True)
        if (event.GetId() == 107):
            self.onglets.availableWineVersionsTreeSelector["x86"].UnselectAll()
            self.onglets.button_rm["x86"].Enable(True)
            self.onglets.button_in["x86"].Enable(False)

    def delete32(self, event):
        self.delete_common(event, "x86")

    def delete_common(self, event, arch):
        version = self.onglets.installedWineVersionsTreeSelector[arch].GetItemText(
            self.onglets.installedWineVersionsTreeSelector[arch].GetSelection())
        used_version = self.checkVersionUse(arch)  # Get the set of wine version used by wineprefix
        message = _('Are you sure you want to delete wine {0}?').format(version)
        if version in used_version:
            message += "\n" + _('This version is CURRENTLY IN USE')
        if (wx.YES == wx.MessageBox(message, os.environ["APPLICATION_TITLE"],
                                    style=wx.YES_NO | wx.ICON_QUESTION)):
            shutil.rmtree(Variables.playonlinux_rep + "/wine/" + fetchUserOS() + "-" + arch + "/" + version)

    def install32(self, event):
        self.install_common(event, "x86")

    def install_common(self, event, arch):
        install = self.onglets.availableWineVersionsTreeSelector[arch].GetItemText(self.onglets.availableWineVersionsTreeSelector[arch].GetSelection())
        subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/install_wver", install, arch])

    def unselect64(self, event):
        if (event.GetId() == 206):
            self.onglets.installedWineVersionsTreeSelector["amd64"].UnselectAll()
            self.onglets.button_rm["amd64"].Enable(False)
            self.onglets.button_in["amd64"].Enable(True)
        if (event.GetId() == 207):
            self.onglets.availableWineVersionsTreeSelector["amd64"].UnselectAll()
            self.onglets.button_rm["amd64"].Enable(True)
            self.onglets.button_in["amd64"].Enable(False)

    def delete64(self, event):
        self.delete_common(event, "amd64")

    def install64(self, event):
        self.install_common(event, "amd64")

    def getVersions(self, arch="x86"):
        if (arch == "x86"):
            self.download32.thread_message = "get"
        if (arch == "amd64"):
            self.download64.thread_message = "get"

    def checkVersionUse(self, arch):  # Check the wine version use by wineprefix
        used_versions = set([])
        prefixes = os.listdir(Variables.playonlinux_rep + "/wineprefix/")  # List of wineprefix
        prefixes.remove('default')  # Remove 'default' (no wine version use by it)
        for prefix in prefixes:
            if playonlinux.GetSettings("ARCH", prefix) == arch:
                wine_version = playonlinux.GetSettings("VERSION", prefix)
                used_versions.add(wine_version)
        return (used_versions)

    def WriteVersion(self, arch="x86"):
        self.onglets.imagesapps[arch].RemoveAll()
        self.onglets.imagesapps_i[arch].RemoveAll()
        self.onglets.availableWineVersionsTreeSelector[arch].DeleteAllItems()
        self.onglets.installedWineVersionsTreeSelector[arch].DeleteAllItems()

        root = self.onglets.availableWineVersionsTreeSelector[arch].AddRoot("")
        self.i = 0
        if (arch == "x86"):
            while (self.i < len(self.download32.versions)):
                self.onglets.imagesapps[arch].Add(
                    wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine-packages.png"))
                self.onglets.availableWineVersionsTreeSelector[arch].AppendItem(root, self.download32.versions[self.i], self.i)
                self.i += 1
        if (arch == "amd64"):
            while (self.i < len(self.download64.versions)):
                self.onglets.imagesapps[arch].Add(
                    wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine-packages.png"))
                self.onglets.availableWineVersionsTreeSelector[arch].AppendItem(root, self.download64.versions[self.i], self.i)
                self.i += 1

        root2 = self.onglets.installedWineVersionsTreeSelector[arch].AddRoot("")
        wfolder = fetchUserOS() + "-" + arch

        used_version = self.checkVersionUse(arch)  # Get the set of wine version used by wineprefix

        installed_versions = os.listdir(Variables.playonlinux_rep + "/wine/" + wfolder)
        installed_versions.sort(key=natsort.natsort_keygen())
        installed_versions.reverse()
        self.i = 0
        self.j = 0
        boldFont = self.GetFont()
        boldFont.SetWeight(wx.BOLD)
        while (self.i < len(installed_versions)):
            if (os.path.isdir(Variables.playonlinux_rep + "/wine/" + wfolder + "/" + installed_versions[self.i])):
                itemId = self.onglets.installedWineVersionsTreeSelector[arch].AppendItem(root2, installed_versions[self.i], self.j)
                if (len(os.listdir(
                        Variables.playonlinux_rep + "/wine/" + wfolder + "/" + installed_versions[self.i])) == 0):
                    self.onglets.imagesapps_i[arch].Add(
                        wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine-warning.png"))
                elif installed_versions[self.i] not in used_version:
                    self.onglets.imagesapps_i[arch].Add(wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine.png"))
                else:  # Clearly show the wine version in use
                    self.onglets.imagesapps_i[arch].Add(
                        wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine-in-use.png"))
                    self.onglets.installedWineVersionsTreeSelector[arch].SetItemFont(itemId, boldFont)
                self.j += 1
            self.i += 1
        try:
            if (versions[0] == "Wine packages website is unavailable"):
                self.onglets.availableWineVersionsTreeSelector[arch].Enable(False)
                self.onglets.imagesapps[arch].RemoveAll()
        except:
            pass
        self.onglets.button_rm[arch].Enable(False)
        self.onglets.button_in[arch].Enable(False)

    def closeapp(self, event):
        self.download32.thread_running = False
        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.download64.thread_running = False

        self.Destroy()

    def Destroy(self):
        self.timer.Stop()
        return super().Destroy()
