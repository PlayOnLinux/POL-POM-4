#!/usr/bin/python3
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

import codecs
import os
import subprocess

import wx
import wx.adv
import wx.html
import wx.lib.agw.hyperlink
from wx.lib.ClickableHtmlWindow import PyClickableHtmlWindow

import lib.Variables as Variables
import lib.playonlinux as playonlinux
from install.DescriptionFetcher import DescriptionFetcher
from install.MiniatureWindow import MiniatureWindow
from ui.PlayOnLinuxWindow import PlayOnLinuxWindow


class InstallWindow(PlayOnLinuxWindow):
    def addCat(self, name, icon, iid):
        espace = 80
        if (os.environ["POL_OS"] == "Mac"):
            offset = 10
        else:
            offset = 2

        self.cats_icons[name] = wx.BitmapButton(self.installWindowHeader, 2000 + iid, wx.Bitmap(icon), (0, 0),
                                                style=wx.NO_BORDER)

        self.cats_links[name] = wx.lib.agw.hyperlink.HyperLinkCtrl(self.installWindowHeader, 3000 + iid, name, pos=(0, 52))
        mataille = self.cats_links[name].GetSize()[0]

        mataille2 = self.cats_icons[name].GetSize()[0]
        image_pos = (espace - mataille2) / 2 + espace * iid;

        self.cats_links[name].SetPosition((espace * iid + (espace - mataille / 1.3) / 2, 47))
        self.cats_icons[name].SetPosition((image_pos, offset))

        self.Bind(wx.lib.agw.hyperlink.EVT_HYPERLINK_LEFT, self.AddApps, id=3000 + iid)
        self.Bind(wx.EVT_BUTTON, self.AddApps, id=2000 + iid)

        self.cats_links[name].SetColours(wx.Colour(0, 0, 0), wx.Colour(0, 0, 0), wx.Colour(0, 0, 0))
        self.cats_links[name].AutoBrowse(False)
        self.cats_links[name].UpdateLink(True)
        self.cats_links[name].SetUnderlines(False, False, False)

        self.cats_links[name].SetFont(self.fontText)
        self.cats_links[name].SetBackgroundColour((255, 255, 255))

    def setWaitState(self, isWaiting):
        if isWaiting:
            self.installWindowCategoryContentPanel.Hide()
            self.panelWait.Show()
            self.manualInstall.Raise()
            self.animation_wait.Play()
            self.installButton.Hide()
            self.updateButton.Hide()
        else:
            self.installWindowCategoryContentPanel.Show()
            self.manualInstall.Raise()
            self.panelWait.Hide()
            self.animation_wait.Stop()
            self.installButton.Show()
            self.updateButton.Show()

        self.Layout()

    def _createHeader(self):
        self.installWindowHeader = wx.Panel(self, -1, size=(802, 69))
        self.installWindowHeader.SetBackgroundColour((255, 255, 255))
        self.windowSizer.Add(self.installWindowHeader, 0, wx.EXPAND)
        self.addCat(_("Accessories"),
                    Variables.playonlinux_env + "/resources/images/install/32/applications-accessories.png", 0)
        self.addCat(_("Development"),
                    Variables.playonlinux_env + "/resources/images/install/32/applications-development.png", 1)
        self.addCat(_("Education"), Variables.playonlinux_env + "/resources/images/install/32/applications-science.png",
                    2)
        self.addCat(_("Games"), Variables.playonlinux_env + "/resources/images/install/32/applications-games.png", 3)
        self.addCat(_("Graphics"), Variables.playonlinux_env + "/resources/images/install/32/applications-graphics.png",
                    4)
        self.addCat(_("Internet"), Variables.playonlinux_env + "/resources/images/install/32/applications-internet.png",
                    5)
        self.addCat(_("Multimedia"),
                    Variables.playonlinux_env + "/resources/images/install/32/applications-multimedia.png", 6)
        self.addCat(_("Office"), Variables.playonlinux_env + "/resources/images/install/32/applications-office.png", 7)
        self.addCat(_("Other"), Variables.playonlinux_env + "/resources/images/install/32/applications-other.png", 8)
        self.addCat(_("Patches"), Variables.playonlinux_env + "/resources/images/install/32/view-refresh.png", 9)

    def _createBody(self):
        self.installWindowBodyPanel = wx.Panel(self, -1)
        self.windowSizer.Add(self.installWindowBodyPanel, 1, wx.EXPAND)
        self.installWindowBodySizer = wx.BoxSizer(wx.VERTICAL)
        self.installWindowBodyPanel.SetSizer(self.installWindowBodySizer)

    def _createWaitPanel(self):
        self.panelWait = wx.Panel(self.installWindowBodyPanel, -1)
        self.installWindowBodySizer.Add(self.panelWait, 1, wx.EXPAND)
        self.panelWait.Hide()
        ## FIXME: Remove those magic numbers
        self.animation_wait = wx.adv.AnimationCtrl(self.panelWait, -1,
                                                   pos=((800 - 128) / 2, (550 - 128) / 2 - 71))
        self.animation_wait.LoadFile(Variables.playonlinux_env + "/resources/images/install/wait.gif")
        self.percentageText = wx.StaticText(self.panelWait, -1, "", ((800 - 30) / 2, (550 - 128) / 2 + 128 + 10 - 71),
                                            wx.DefaultSize)
        self.percentageText.SetFont(self.fontTitle)
        self.timer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.TimerAction, self.timer)
        self.timer.Start(200)

    def _createInstallWindowCategoryContentPanel(self):
        self.installWindowCategoryContentPanel = wx.Panel(self.installWindowBodyPanel, -1)

        self.installWindowBodySizer.Add(self.installWindowCategoryContentPanel, 1, wx.EXPAND)
        self.installWindowCategoryContentSizer = wx.BoxSizer(wx.VERTICAL)
        self.installWindowCategoryContentPanel.SetSizer(self.installWindowCategoryContentSizer)

    def _createFilterPanel(self):
        self.filterPanel = wx.Panel(self.installWindowCategoryContentPanel, -1)

        self.installWindowCategoryContentSizer.AddSpacer(10)
        self.installWindowCategoryContentSizer.Add(self.filterPanel, 0, wx.EXPAND)
        self.installWindowCategoryContentSizer.AddSpacer(10)

        filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.filterPanel.SetSizer(filterSizer)

        self.searchbox = wx.SearchCtrl(self.filterPanel, 110,)
        filtersCaption = wx.StaticText(self.filterPanel, -1, _("Include:"))
        self.testingChk = wx.CheckBox(self.filterPanel, 401)
        self.testingChk.SetValue(True)
        testingCaption = wx.StaticText(self.filterPanel, -1, _("Testing"))
        self.nocdChk = wx.CheckBox(self.filterPanel, 402)
        nocdCaption = wx.StaticText(self.filterPanel, -1, _("No-cd needed"))
        self.commercialChk = wx.CheckBox(self.filterPanel, 403)
        self.commercialChk.SetValue(True)
        commercialCaption = wx.StaticText(self.filterPanel, -1, _("Commercial"))
        self.panelStars = wx.Panel(self.filterPanel, -1)

        filterSizer.AddSpacer(10)
        filterSizer.Add(self.searchbox, 4, wx.EXPAND)
        filterSizer.AddSpacer(10)
        filterSizer.Add(filtersCaption, 0, wx.EXPAND)
        filterSizer.AddSpacer(10)
        filterSizer.Add(self.testingChk, 0, wx.EXPAND)
        filterSizer.Add(testingCaption, 0, wx.EXPAND)
        filterSizer.AddSpacer(10)
        filterSizer.Add(self.nocdChk, 0, wx.EXPAND)
        filterSizer.Add(nocdCaption, 0, wx.EXPAND)
        filterSizer.AddSpacer(10)
        filterSizer.Add(self.commercialChk, 0, wx.EXPAND)
        filterSizer.Add(commercialCaption, 0, wx.EXPAND)
        filterSizer.AddSpacer(20)
        filterSizer.Add(self.panelStars, 2, wx.EXPAND)

        filterSizer.AddSpacer(10)

    def _createAppNavigation(self):
        self.appNavigationPanel = wx.Panel(self.installWindowCategoryContentPanel, -1)
        self.installWindowCategoryContentSizer.Add(self.appNavigationPanel, 10, wx.EXPAND)
        self.appNavigationSizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.appNavigationPanel.SetSizer(self.appNavigationSizer)

        self.imagesapps = wx.ImageList(22, 22)
        self.appsList = wx.TreeCtrl(self.appNavigationPanel, 106,
                                    style=wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | Variables.widget_borders)
        self.appsList.SetImageList(self.imagesapps)
        self.appsList.SetSpacing(0)

        self.appNavigationSizer.AddSpacer(10)
        self.appNavigationSizer.Add(self.appsList, 4, wx.EXPAND, 5)
        self.appNavigationSizer.AddSpacer(10)

    def _createAppDescription(self):
        appDescriptionPanel = wx.Panel(self.appNavigationPanel, -1)
        self.appNavigationSizer.Add(appDescriptionPanel, 1, wx.EXPAND)
        self.appNavigationSizer.AddSpacer(10)

        appDescriptionSizer = wx.BoxSizer(wx.VERTICAL)

        self.descriptionContentHtmlBox = PyClickableHtmlWindow(appDescriptionPanel, 107, style=Variables.widget_borders)
        appDescriptionSizer.Add(self.descriptionContentHtmlBox, 1, wx.EXPAND)

        self.descriptionLoaderPanel = wx.Panel(appDescriptionPanel, -1, style=Variables.widget_borders)
        self.descriptionLoaderPanel.SetBackgroundColour((255, 255, 255))
        self.animation = wx.adv.AnimationCtrl(self.descriptionLoaderPanel, -1, pos=(90, 100))
        self.animation.LoadFile(Variables.playonlinux_env + "/resources/images/install/wait_mini.gif")
        self.animation.Hide()
        self.descriptionLoaderPanel.Hide()

        self.image = wx.StaticBitmap(appDescriptionPanel, 108,
                                     wx.Bitmap(Variables.playonlinux_env + "/resources/images/pol_min.png"))
        self.image.Bind(wx.EVT_LEFT_DOWN, self.sizeUpScreen)

        appDescriptionSizer.Add(self.descriptionLoaderPanel, 1, wx.EXPAND)
        appDescriptionSizer.AddSpacer(10)
        appDescriptionSizer.Add(self.image, 0)
        appDescriptionPanel.SetSizer(appDescriptionSizer)

    def _createButtons(self):
        buttonsPanel = wx.Panel(self.installWindowBodyPanel, -1)
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsPanel.SetSizer(buttonsSizer)

        self.installWindowBodySizer.AddSpacer(10)
        self.installWindowBodySizer.Add(buttonsPanel, 0, wx.EXPAND)
        self.installWindowBodySizer.AddSpacer(10)

        self.cancelButton = wx.Button(buttonsPanel, wx.ID_CLOSE, _("Cancel"))
        self.installButton = wx.Button(buttonsPanel, wx.ID_APPLY, _("Install"))
        self.updateButton = wx.Button(buttonsPanel, wx.ID_REFRESH, _("Refresh"))
        self.manualInstall = wx.lib.agw.hyperlink.HyperLinkCtrl(buttonsPanel, 111, _("Install a non-listed program"))
        self.manualInstall.SetColours(wx.Colour(0, 0, 0), wx.Colour(0, 0, 0), wx.Colour(0, 0, 0))
        self.manualInstall.AutoBrowse(False)
        self.manualInstall.UpdateLink(True)

        buttonsSizer.AddSpacer(10)
        buttonsSizer.Add(self.manualInstall, 0)
        buttonsSizer.AddStretchSpacer()

        buttonsSizer.Add(self.updateButton, 0)
        buttonsSizer.AddSpacer(1)
        buttonsSizer.Add(self.cancelButton, 0)
        buttonsSizer.AddSpacer(1)
        buttonsSizer.Add(self.installButton, 0)
        buttonsSizer.AddSpacer(10)

    def __init__(self, parent, id, title):
        PlayOnLinuxWindow.__init__(self, parent, -1, title, size=(850, 550))
        self.cats_icons = {}
        self.cats_links = {}

        self.descriptionFetcher = DescriptionFetcher()

        ## Window
        self.windowSizer = wx.BoxSizer(wx.VERTICAL)
        self._createHeader()
        self._createBody()
        self.SetSizer(self.windowSizer)

        self._createInstallWindowCategoryContentPanel()
        self._createWaitPanel()

        # Filter panel
        self._createFilterPanel()

        # Apps Navigation
        self._createAppNavigation()
        self._createAppDescription()

        ## Buttons
        self._createButtons()

        self.live = 0
        self.openMin = False
        self.images_cat = wx.ImageList(22, 22)

        self.installButton.Enable(False)


        # wx.EVT_TREE_SEL_CHANGED(self, 105, self.AddApps)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.AppsDetails, id=106)
        self.Bind(wx.EVT_BUTTON, self.closeapp, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.installapp, id=wx.ID_APPLY)
        self.Bind(wx.EVT_BUTTON, self.UpdatePol, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_CLOSE, self.closeapp)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.installapp, id=106)
        self.Bind(wx.EVT_TEXT, self.search, id=110)
        self.Bind(wx.lib.agw.hyperlink.EVT_HYPERLINK_LEFT, self.manual, id=111)

        self.Bind(wx.EVT_CHECKBOX, self.CheckBoxReload, id=401)
        self.Bind(wx.EVT_CHECKBOX, self.CheckBoxReload, id=402)
        self.Bind(wx.EVT_CHECKBOX, self.CheckBoxReload, id=403)

    def TimerAction(self, event):
        try:
            self.lasthtml_content
        except AttributeError:
            self.lasthtml_content = ""

        if self.lasthtml_content != self.descriptionFetcher.htmlContent:
            self.SetImg(self.descriptionFetcher.miniature)
            self.descriptionFetcher.miniature = self.descriptionFetcher.miniature_defaut

            self.lasthtml_content = self.descriptionFetcher.htmlContent
            if self.descriptionFetcher.htmlContent == "###WAIT###":
                self.animation.Show()
                self.animation.Play()
                self.descriptionLoaderPanel.Show()
                self.descriptionContentHtmlBox.Hide()
                self.Refresh()
            else:
                self.animation.Stop()
                self.descriptionContentHtmlBox.Show()
                self.animation.Hide()
                self.descriptionLoaderPanel.Hide()
                self.Refresh()
                self.descriptionContentHtmlBox.SetPage(self.descriptionFetcher.htmlContent)
            self.Layout()

        self.showStars(self.descriptionFetcher.stars)

        if self.openMin == True:
            if self.descriptionFetcher.med_miniature != None:
                self.miniatureWindow = MiniatureWindow(None, -1,
                                                       self.appsList.GetItemText(self.appsList.GetSelection()),
                                                       self.descriptionFetcher.med_miniature)
                self.miniatureWindow.Show()
                self.miniatureWindow.Center(wx.BOTH)
                self.openMin = False

    def closeapp(self, event):
        self.descriptionFetcher.thread_running = False
        self.Destroy()

    def manual(self, event):
        self.live = 1
        self.installapp(self)

    def showStars(self, stars):
        starWidth = 20
        self.panelStars.DestroyChildren()

        for i in range(int(stars)):
            wx.StaticBitmap(self.panelStars, -1,
                            wx.Bitmap(Variables.playonlinux_env + "/etc/star.png"),
                            (i * starWidth, 0), wx.DefaultSize)

    def UpdatePol(self, event):
        self.DelApps()
        self.Parent.updater.check()
        playonlinux.SetSettings("LAST_TIMESTAMP", "0")

    def installapp(self, event):
        if (self.live == 1):
            InstallApplication = "ExecLiveInstall"
        else:
            InstallApplication = self.appsList.GetItemText(self.appsList.GetSelection())

        if os.path.exists(Variables.playonlinux_rep + "/configurations/listes/search"):
            content = codecs.open(Variables.playonlinux_rep + "/configurations/listes/search", "r",
                                  "utf-8").read().split("\n")
            found = False
            for line in content:
                split = line.split("~")
                if (split[0] == InstallApplication):
                    found = True
                    break;
            if (found == True):
                if (len(split) <= 1):
                    self.UpdatePol(self)
                else:
                    if (split[1] == "1"):
                        wx.MessageBox(_(
                            "This program is currently in testing.\n\nIt might not work as expected. Your feedback, positive or negative, is specially important to improve this installer."),
                            _("Please read this"))
                    if (split[2] == "1"):
                        wx.MessageBox(_(
                            "This program contains a protection against copy (DRM) incompatible with emulation.\nThe only workaround is to use a \"no-cd\" patch, but since those can also be used for piracy purposes we won't give any support on this matter."),
                            _("Please read this"))

        subprocess.Popen(
            ["bash", Variables.playonlinux_env + "/bash/install", InstallApplication])

        self.Destroy()
        return

    def search(self, event):
        self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/search", 'r', "utf-8")
        self.apps = self.apps.readlines()
        self.j = 0
        while (self.j < len(self.apps)):
            self.apps[self.j] = self.apps[self.j].replace("\n", "")
            self.j += 1

        self.j = 0
        self.k = 0
        self.user_search = self.searchbox.GetValue()
        self.search_result = []

        while (self.j < len(self.apps)):
            if (self.user_search.lower() in self.apps[self.j].lower()):
                self.search_result.append(self.apps[self.j])
                self.k = self.k + 1
            self.j = self.j + 1

        if (len(self.user_search) < 2 or "~" in self.user_search):
            self.search_result = []
        self.user_search_cut = self.user_search.split(":")
        if (len(self.user_search_cut) > 1):
            if (self.user_search_cut[0] == "get" and self.user_search_cut[1].isdigit()):
                self.search_result.append(self.user_search)

        if (self.user_search != ""):
            self.WriteApps(self.search_result)
        else:
            self.DelApps()

    def EraseDetails(self):
        self.descriptionContentHtmlBox.SetValue("")

    def AppsDetails(self, event):
        self.installButton.Enable(True)
        self.application = self.appsList.GetItemText(self.appsList.GetSelection())
        self.descriptionFetcher.download(self.application)

    def sizeUpScreen(self, event):
        self.openMin = True

    def WriteApps(self, array):
        self.imagesapps.RemoveAll()

        self.DelApps()
        self.root_apps = self.appsList.AddRoot("")
        self.i = 0
        array.sort(key=str.upper)
        for app in array:
            app_array = app.split("~")
            appname = app_array[0]
            try:
                free = int(app_array[3])
                testing = int(app_array[1])
                nocd = int(app_array[2])
            except IndexError:
                free = 0
                testing = 0
                nocd = 0

            show = True
            if nocd == 1 and self.nocdChk.IsChecked() == 0:
                show = False
            if free == 0 and self.commercialChk.IsChecked() == 0:
                show = False
            if testing == 1 and self.testingChk.IsChecked() == 0:
                show = False

            if (show == True):
                self.icon_look_for = Variables.playonlinux_rep + "/configurations/icones/" + appname
                if (os.path.exists(self.icon_look_for)):
                    try:
                        bitmap = wx.Image(self.icon_look_for)
                        bitmap.Rescale(22, 22, wx.IMAGE_QUALITY_HIGH)
                        bitmap = bitmap.ConvertToBitmap()
                        self.imagesapps.Add(bitmap)
                    except:
                        pass
                else:
                    self.imagesapps.Add(wx.Bitmap(Variables.playonlinux_env + "/etc/playonlinux22.png"))
                itemId = self.appsList.AppendItem(self.root_apps, appname, self.i)
                if testing == 1:
                    # (255,255,214) is web site color for beta, but it's not very visible next to plain white,
                    # and red is the color of danger
                    self.appsList.SetItemBackgroundColour(itemId, (255, 214, 214))
                self.i = self.i + 1

    def DelApps(self):
        self.appsList.DeleteAllItems()

    def SetImg(self, image):
        self.image.SetBitmap(wx.Bitmap(image))
        self.Refresh()

    def ResetImg(self):
        self.SetImg(Variables.playonlinux_env + "/resources/images/pol_min.png")

    def CheckBoxReload(self, event):
        chk_id = event.GetId()
        if (chk_id == 401):
            if (self.testingChk.IsChecked() == 1):
                wx.MessageBox(_(
                    "By enabling this option, you can install programs that employ digital rights management (DRM) copy protection that are not supported by {0} and might need to be bypassed.\n\nThis feature should not be construed as implicit or implied condoning of piracy and as such, we will not offer any support for issues resulting from using this option.").format(
                    os.environ["APPLICATION_TITLE"]), _("Attention!"))
        if (chk_id == 402):
            if (self.nocdChk.IsChecked() == 1):
                wx.MessageBox(_(
                    "By enabling this, you will have access to installers for programs that contain protections against copy (DRM) incompatible with emulation.\nThe only workaround is to use \"no-cd\" patches, but since those can also be used for piracy purposes we won't give any support on this matter."),
                    _("Please read this"))

        if (self.searchbox.GetValue() == ""):
            self.AddApps(self, noevent=True)
        else:
            self.search(self)

    def AddApps(self, event, noevent=False):
        self.searchbox.SetValue("")
        if (noevent == False):
            if (event.GetId() >= 3000):
                self.cat_selected = event.GetId() - 3000
            else:
                self.cat_selected = event.GetId() - 2000

            self.current_cat = self.cat_selected
        else:
            try:
                self.cat_selected = self.current_cat
            except:
                return 0
        if (self.cat_selected == 8):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/0", 'r', "utf-8")
        if (self.cat_selected == 3):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/1", 'r', "utf-8")
        if (self.cat_selected == 0):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/2", 'r', "utf-8")
        if (self.cat_selected == 7):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/3", 'r', "utf-8")
        if (self.cat_selected == 5):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/4", 'r', "utf-8")
        if (self.cat_selected == 6):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/5", 'r', "utf-8")
        if (self.cat_selected == 4):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/6", 'r', "utf-8")
        if (self.cat_selected == 1):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/7", 'r', "utf-8")
        if (self.cat_selected == 2):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/8", 'r', "utf-8")
        if (self.cat_selected == 9):
            self.apps = codecs.open(Variables.playonlinux_rep + "/configurations/listes/9", 'r', "utf-8")

        if (self.cat_selected != -1):
            self.apps = self.apps.readlines()
            self.j = 0
            while (self.j < len(self.apps)):
                self.apps[self.j] = self.apps[self.j].replace("\n", "")
                self.j += 1
            self.WriteApps(self.apps)

    def Destroy(self):
        self.timer.Stop()
        super().Destroy()
