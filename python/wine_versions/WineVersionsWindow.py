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
from wine_versions.WineVersionsTools import fetchUserOS, fetch_supported_archs

lib.lng.Lang()


class WineVersionsWindow(wx.Frame):
    def on_available_wine_versions_downloaded(self, versions_per_architecture):
        for architecture in versions_per_architecture:
            if architecture in fetch_supported_archs():
                available_versions = []
                for version in versions_per_architecture[architecture]:
                    available_versions.append(version["name"])

                available_versions.sort(key=natsort.natsort_keygen())
                available_versions.reverse()
                available_versions = available_versions[:]

                for version in available_versions:
                    wx.CallAfter(self.notebook.add_available_version, architecture, version)

    def on_installed_wine_versions_downloaded(self, versions_per_architecture):
        for architecture in versions_per_architecture:
            if architecture in fetch_supported_archs():
                installed_versions = []
                for version in versions_per_architecture[architecture]:
                    installed_versions.append(version["name"])

                installed_versions.sort(key=natsort.natsort_keygen())
                installed_versions.reverse()
                installed_versions = installed_versions[:]

                for version in installed_versions:
                    wx.CallAfter(self.notebook.add_installed_version, architecture, version)

    def handle_error(self, error):
        print(error)

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self,
                          parent,
                          -1,
                          title,
                          size=(750, 400 + Variables.windows_add_size),
                          style=wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
        self.timer = wx.Timer(self, 1)
        self.SetIcon(wx.Icon(Variables.playonlinux_env + "/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.wine_version_fetcher = WineVersionFetcher(fetchUserOS())

        self.notebook = WineVersionsNotebook(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.notebook, 15, wx.EXPAND | wx.ALL, 2)

        for available_arch in fetch_supported_archs():
            self.notebook.add_architecture_tab(available_arch)

        self.last_checksum = None
        self.notebook.on_install_handler = self.install_wine_version
        self.notebook.on_remove_handler = self.remove_wine_version

        self.Bind(wx.EVT_TIMER, self.detect_changes, self.timer)
        self.timer.Start(1000)

    def refresh(self):
        for available_arch in fetch_supported_archs():
            self.notebook.clean_version_of_architecture(available_arch)

        self.wine_version_fetcher.fetch_all_available_wine_version(self.on_available_wine_versions_downloaded, self.handle_error)
        self.wine_version_fetcher.fetch_all_installed_wine_version(self.on_installed_wine_versions_downloaded, self.handle_error)

    def detect_changes(self, event):
        checksum = self.wine_version_fetcher.calculate_installed_hash()

        if self.last_checksum != checksum:
            self.last_checksum = checksum
            self.refresh()


    def remove_wine_version(self, architecture, version):
        used_version = self.checkVersionUse(architecture)  # Get the set of wine version used by wineprefix
        message = _('Are you sure you want to delete wine {0}?').format(version)
        if version in used_version:
            message += "\n" + _('This version is CURRENTLY IN USE')
        if (wx.YES == wx.MessageBox(message, os.environ["APPLICATION_TITLE"],
                                    style=wx.YES_NO | wx.ICON_QUESTION)):
            shutil.rmtree(Variables.playonlinux_rep + "/wine/" + fetchUserOS() + "-" + architecture + "/" + version)


    def install_wine_version(self, architecture, version):
        print("%s of architecture %s will be installed " % (version, architecture))
        subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/install_wver", version, architecture])


    def checkVersionUse(self, arch):  # Check the wine version use by wineprefix
        used_versions = set([])
        prefixes = os.listdir(Variables.playonlinux_rep + "/wineprefix/")  # List of wineprefix
        prefixes.remove('default')  # Remove 'default' (no wine version use by it)
        for prefix in prefixes:
            if playonlinux.GetSettings("ARCH", prefix) == arch:
                wine_version = playonlinux.GetSettings("VERSION", prefix)
                used_versions.add(wine_version)
        return (used_versions)


    def close(self, event):
        self.download32.thread_running = False
        if (os.environ["AMD64_COMPATIBLE"] == "True"):
            self.download64.thread_running = False

        self.Destroy()

    def Destroy(self):
        self.timer.Stop()
        return super().Destroy()
