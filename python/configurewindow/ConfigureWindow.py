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

import os
import shutil
import stat

import subprocess
import wx

import lib.Variables as Variables
import lib.playonlinux as playonlinux
from configurewindow.ConfigureWindowNotebook import ConfigureWindowNotebook

## TODO: Terminate refactoring this module
class ConfigureWindow(wx.Frame):
    def __init__(self,parent,id,title,shortcut, isPrefix = False):
        wx.Frame.__init__(self, parent, -1, title, size = (800, 455+Variables.windows_add_size))
        self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.SetTitle(_('{0} configuration').format(os.environ["APPLICATION_TITLE"]))

        self.windowSplitter = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER)

        self.panelEmpty = wx.Panel(self.windowSplitter, -1)
        self.onglets = ConfigureWindowNotebook(self.windowSplitter)

        self.noselect = wx.StaticText(self.panelEmpty, -1, _('Please select a program or a virtual drive to configure'),pos=(0,150),style=wx.ALIGN_RIGHT)
        self.noselect.SetPosition(((600-self.noselect.GetSize()[0])/2,150))

        self.noselect.Wrap(600)
        if(isPrefix == True):
            self.onglets.s_isPrefix = True
            self.onglets.s_prefix = shortcut
        else:
            self.onglets.s_isPrefix = False
            self.onglets.s_title = shortcut

        self.images = wx.ImageList(16, 16)

        self.leftPanel = wx.Panel(self.windowSplitter, -1)
        self.leftPanelSizer = wx.BoxSizer(wx.VERTICAL)
        self.leftPanel.SetSizer(self.leftPanelSizer)

        self.list_game = wx.TreeCtrl(self.leftPanel, 900, size = wx.DefaultSize, style=wx.TR_HIDE_ROOT)
        self.leftPanelSizer.Add(self.list_game, 1, wx.EXPAND)

        self.prefixPanel = wx.Panel(self.leftPanel, -1)
        self.leftPanelSizer.Add(self.prefixPanel, 0, wx.EXPAND)

        if(os.environ["POL_OS"] == "Mac"):
            self.AddPrefix = wx.Button(self.prefixPanel, 1001, _("New"), pos=(0, -8), size=(93, 30))
            self.DelPrefix = wx.Button(self.prefixPanel, 1002, _("Remove"), pos=(98, -8), size=(93, 30))
        else:
            self.AddPrefix = wx.Button(self.prefixPanel, 1001, _("New"), pos=(0, 0), size=(95, 25))
            self.DelPrefix = wx.Button(self.prefixPanel, 1002, _("Remove"), pos=(100, 0), size=(95, 25))

        self.Bind(wx.EVT_BUTTON, self.NewPrefix, id=1001)
        self.Bind(wx.EVT_BUTTON, self.DeletePrefix, id=1002)


        self.list_game.SetSpacing(0)
        self.list_game.SetImageList(self.images)


        self.windowSplitter.SplitVertically(self.leftPanel, self.panelEmpty)
        self.windowSplitter.SetSashPosition(200)

        self.onglets.General(_("General"))
        self.onglets.Wine("Wine")
        self.onglets.Packages(_("Install components"))
        self.onglets.Display(_("Display"))
        self.onglets.Miscellaneous(_("Miscellaneous"))

        self.list_software()

        self.onglets.panelGeneral.Bind(wx.EVT_LEFT_UP, self.onglets.ReleaseTyping)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.change_program_to_selection, id=900)

        self.timer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.AutoReload, self.timer)

        self.timer.Start(500)
        self.oldreload = None
        self.oldimg = None
        self.oldpref = None
        self.oldver32 = None
        self.olderver64 = None
        self.AutoReload(self)

    def NewPrefix(self, event):
        subprocess.Popen(["bash", Variables.playonlinux_env+"/bash/create_prefix"])

    def DeletePrefix(self, event):
        if(self.onglets.s_isPrefix == True):
            if(self.onglets.s_prefix == "default"):
                wx.MessageBox(_("This virtual drive is protected"), os.environ["APPLICATION_TITLE"])
            else:
                if(wx.YES == wx.MessageBox(_("Are you sure you want to delete {0} virtual drive ?").format(self.onglets.s_prefix), os.environ["APPLICATION_TITLE"], style=wx.YES_NO | wx.ICON_QUESTION)):
                    mylist = os.listdir(Variables.playonlinux_rep+"/shortcuts")
                    for element in mylist:
                        if(playonlinux.getPrefix(element).lower() == self.onglets.s_prefix.lower()):
                            subprocess.Popen(["bash", Variables.playonlinux_env+"/bash/uninstall", "--non-interactive", element])
                    self._delete_directory(Variables.playonlinux_rep+"/wineprefix/"+self.onglets.s_prefix)
        else:
            if(wx.YES == wx.MessageBox(_("Are you sure you want to delete {0} ?").format(self.onglets.s_title), os.environ["APPLICATION_TITLE"], style=wx.YES_NO | wx.ICON_QUESTION)):
                subprocess.Popen(["bash", Variables.playonlinux_env+"/bash/uninstall", "--non-interactive", self.onglets.s_title])

        self.onglets.s_isPrefix = True
        self.change_program("default",True)
        self.list_game.SelectItem(self.prefixes_item["default"])

    def _delete_directory(self, root_path):
        """
        Remove a directory tree, making sure no directory rights get in the way.
        It assumes everything is owned by the user however.
        """

        # Handle symlink
        if os.path.islink(root_path):
            os.remove(root_path)
            # Shall we warn the user that the target prefix has not been cleared?
        else:
            # need exec right to dereference content
            # need read right to list content
            # need write right to remove content
            needed_dir_rights = stat.S_IXUSR|stat.S_IRUSR|stat.S_IWUSR

            # topdown=True, the default, is necessary to fix directories rights
            # before trying to list them
            for dirname, dirs, files in os.walk(root_path):
                for dir in dirs:
                    fullpath = os.path.join(dirname, dir)
                    # To speed up the process, only modify metadata when necessary
                    attr = os.lstat(fullpath)
                    if attr.st_mode & needed_dir_rights != needed_dir_rights:
                        print("%s rights need fixing" % fullpath)
                        os.chmod(fullpath, needed_dir_rights)

            # Alright, now we should be able to proceed
            shutil.rmtree(root_path)

    def AutoReload(self, event):
        if(self.onglets.typing == False):
            reload = os.path.getmtime(Variables.playonlinux_rep+"/shortcuts")
            if(reload != self.oldreload):
                self.list_software()
                self.oldreload = reload

            reloadimg = os.path.getmtime(Variables.playonlinux_rep+"/icones/32")
            if(reloadimg != self.oldimg):
                self.list_software()
                self.oldimg = reloadimg

            reloadpref = os.path.getmtime(Variables.playonlinux_rep+"/wineprefix")
            if(reloadpref != self.oldpref):
                self.list_software()
                self.oldpref = reloadpref

            reloadver32 = os.path.getmtime(Variables.playonlinux_rep+"/wine/"+Variables.os_name+"-x86/")
            reloadver64 = os.path.getmtime(Variables.playonlinux_rep+"/wine/"+Variables.os_name+"-amd64/")

            if(reloadver32 != self.oldver32 or reloadver64 != self.oldver64):
                self.oldver32 = reloadver32
                self.oldver64 = reloadver64
                self.onglets.UpdateVersions(self.onglets.arch)

    def change_program_to_selection(self, event):
        parent =  self.list_game.GetItemText(self.list_game.GetItemParent(self.list_game.GetSelection()))
        self.current_sel = self.list_game.GetItemText(self.list_game.GetSelection())

        if(parent == "#ROOT#"):
            self.onglets.s_isPrefix = True
        else:
            self.onglets.s_isPrefix = False

        self.change_program(self.current_sel,self.onglets.s_isPrefix)

    def change_program(self, new_prgm,isPrefix = False):
        self.onglets.changing_selection = True
        if(isPrefix == True):
            self.onglets.s_isPrefix = True
            try:
                if(self.current_sel == "default"):
                    self.windowSplitter.Unsplit()
                    self.windowSplitter.SplitVertically(self.leftPanel, self.panelEmpty)
                    self.windowSplitter.SetSashPosition(200)
                else:
                    self.windowSplitter.Unsplit()
                    self.windowSplitter.SplitVertically(self.leftPanel, self.onglets)
                    self.windowSplitter.SetSashPosition(200)
            except AttributeError:
                self.windowSplitter.Unsplit()
                self.windowSplitter.SplitVertically(self.leftPanel, self.panelEmpty)
                self.windowSplitter.SetSashPosition(200)
        else:
            self.windowSplitter.Unsplit()
            self.windowSplitter.SplitVertically(self.leftPanel, self.onglets)
            self.windowSplitter.SetSashPosition(200)
        self.onglets.UpdateValues(new_prgm)
        self.Refresh()
        self.SetFocus()
        try:
            self.GetTopWindow().Raise()
        except:
            pass

    def list_software(self):
        self.games = os.listdir(Variables.playonlinux_rep+"shortcuts/")
        self.games.sort()

        self.prefixes = os.listdir(Variables.playonlinux_rep+"wineprefix/")
        self.prefixes.sort()

        self.games_item = {}
        self.prefixes_item = {}

        try:
            self.games.remove(".DS_Store")
        except:
            pass

        try:
            self.prefixes.remove(".DS_Store")
        except:
            pass

        self.list_game.DeleteAllItems()
        self.images.RemoveAll()
        root = self.list_game.AddRoot("#ROOT#")

        self.i = 0
        for prefix in self.prefixes:
            if(os.path.isdir(Variables.playonlinux_rep+"wineprefix/"+prefix)):
                self.prefixes_item[prefix] = self.list_game.AppendItem(root, prefix, self.i)

                if(os.path.exists(Variables.playonlinux_rep+"/wineprefix/"+prefix+"/icon")):
                    self.file_icone = Variables.playonlinux_rep+"/wineprefix/"+prefix+"/icon"
                else:
                    try:
                        archdd = playonlinux.GetSettings('ARCH',prefix)
                        if(archdd == "amd64"):
                            archdd = "64"
                        else:
                            archdd = "32"
                    except:
                        archdd = "32"
                    self.file_icone = Variables.playonlinux_env+"/resources/images/menu/virtual_drive_"+archdd+".png"

                try:
                    self.bitmap = wx.Image(self.file_icone)
                    self.bitmap.Rescale(16,16,wx.IMAGE_QUALITY_HIGH)
                    self.bitmap = self.bitmap.ConvertToBitmap()
                    self.images.Add(self.bitmap)
                except:
                    pass

                self.list_game.SetItemBold(self.prefixes_item[prefix], True)

                for game in self.games: #METTRE EN 32x32
                    if(playonlinux.getPrefix(game).lower() == prefix.lower()):
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
                        self.i += 1
                        self.games_item[game] = self.list_game.AppendItem(self.prefixes_item[prefix], game, self.i)

                self.i += 1

        self.list_game.ExpandAll()
        try:
            if(self.onglets.s_isPrefix == True):
                self.list_game.SelectItem(self.prefixes_item[self.onglets.s_prefix])
            else:
                self.list_game.SelectItem(self.games_item[self.onglets.s_title])
        except:
            self.onglets.s_isPrefix = True
            self.change_program("default",True)
            self.list_game.SelectItem(self.prefixes_item["default"])

    def app_Close(self, event):
        self.Destroy()

    def apply_settings(self, event):
        self.Destroy()

    def Destroy(self):
        self.timer.Stop()
        return super().Destroy()
