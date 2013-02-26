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

import os, sys, string, shutil
import wx, time
#from subprocess import Popen,PIPE

import wine_versions
import lib.playonlinux as playonlinux
import lib.wine as wine
import lib.Variables as Variables
import lib.lng as lng
import lib.irc as irc
from wx.lib.ClickableHtmlWindow import PyClickableHtmlWindow

class Onglets(wx.Notebook):
    # Classe dérivée du wx.Notebook
    def __init__(self, parent):
        self.notebook = wx.Notebook.__init__(self, parent, -1)

    def getSettings(self): # Faudra revoir ça dans une future version
        irc_settings = {}

        if(os.environ["POL_OS"] == "Linux"):
            irc_settings['NICKNAME'] = os.environ["USER"]+"-pol"
        else:
            irc_settings['NICKNAME'] = os.environ["USER"]+"-pom"

        irc_settings['AUTOCONNECT'] = "0"
        irc_settings['ALERT'] = "0"
        irc_settings["PLAYSOUND"] = "1"
        if(os.path.exists(Variables.playonlinux_rep+"/configurations/options/irc")):
            ircfile = open(Variables.playonlinux_rep+"/configurations/options/irc","r").readlines()
            self.i = 0

            while(self.i < len(ircfile)):
                line_parsed = string.split(ircfile[self.i].replace("\n","").replace("\r",""),"=")
                irc_settings[line_parsed[0]] = line_parsed[1]
                self.i += 1
        return irc_settings

    def selectChanByText(self, text):
        self.item = self.root_window

        self.ij = 0
        self.texte = None
        while(self.texte != text):
            if(self.ij >= len(irc.chans)):
                return self.window.GetLastChild(self.root_window)

            self.item = self.window.GetNextVisible(self.item)
            self.texte = self.window.GetItemText(self.item)
            self.ij += 1


        return self.item

    def OpenWindow(self):
        #if(nom.lower() not in irc.chans and not "@" in nom and nom != "freenode-connect"):
        #self.old_selection = self.window.GetItemText(self.window.GetSelection())
        self.window.DeleteAllItems()
        self.root_window = self.window.AddRoot("")
        self.i = 0
        while(self.i < len(irc.chans)):
            nom = irc.chans[self.i].lower()
            if("." not in nom and nom != "freenode-connect"):
                if("#" in nom):
                    self.window.AppendItem(self.root_window, nom, 0)
                else:
                    if(nom.lower() == "nickserv" or nom.lower() == "chanserv" or nom.lower() == "botserv"):
                        self.window.AppendItem(self.root_window, nom, 2)
                    else:
                        if(nom.lower() == "playonlinux"):
                            self.window.AppendItem(self.root_window, nom, 3)
                        else:
                            self.window.AppendItem(self.root_window, nom, 1)
                #if(self.i == 0):
                    #self.window.SelectItem(self.window.GetLastChild(self.root_window))
            self.i += 1
        #item = self.selectChanByText(self.old_selection)
        #self.window.SelectItem(item)
            #irc.open_window.append(nom.lower())

    def selectWindow(self, name):
        item = self.selectChanByText(name)
        self.window.SelectItem(item)

    def AjouteIRC(self, nom):
        self.panel = wx.Panel(self, -1)
        self.panels_button = wx.Panel(self.panel, -1)
        self.panels_main = wx.Panel(self.panel, -1)
        self.panels_connexion = wx.Panel(self.panel, -1)
        #self.content =  wx.TextCtrl(self.panel, 107, pos=(0,20), size=(500,300), style = wx.TE_MULTILINE | wx.TE_RICH2 | wx.CB_READONLY | wx.RAISED_BORDER)

        self.content = PyClickableHtmlWindow(self.panels_main, -1, style=wx.RAISED_BORDER)
        self.buddy = wx.TreeCtrl(self.panels_main, 126, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|wx.RAISED_BORDER)
        self.buddy.SetSpacing(0);

        self.window = wx.TreeCtrl(self.panels_main, 127, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|wx.RAISED_BORDER)
        #self.root_window = self.window.AddRoot("")
        self.window.SetSpacing(0);

        self.buddy_images = wx.ImageList(16, 16)
        self.buddy_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/star.png"));
        self.buddy_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/h-star.png"));
        self.buddy_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/playonlinux16.png"));
        self.buddy_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/spacer16.png"));
        self.buddy_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/install/star.png"));
        self.buddy.SetImageList(self.buddy_images)

        self.window_images = wx.ImageList(16,16)
        self.window_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/internet-group-chat.png"));
        self.window_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/system-users.png"));
        self.window_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/onglet/applications-system.png"));
        self.window_images.Add(wx.Bitmap(Variables.playonlinux_env+"/etc/playonlinux16.png"));
        self.window.SetImageList(self.window_images)

        self.buddy.SetSpacing(0);
        self.field =  wx.TextCtrl(self.panels_button, 121, style = wx.TE_MULTILINE)
        self.button = wx.Button(self.panels_button, 122, _("Send"))
        self.connect = wx.Button(self.panels_connexion, 123, _("Connect"), pos=(0,0), size=(150,28))
        self.disconnect = wx.Button(self.panels_connexion, 124, _("Disconnect"), pos=(0,0), size=(150,28))
        self.close = wx.Button(self.panels_connexion, 128, _("Leave"), pos=(155,0), size=(150,28))
        #self.close = wx.BitmapButton(self.panels_connexion, 128, wx.Bitmap(Variables.playonlinux_env+"/resources/images/menu/wineserver.png"), pos=(630,0))
        self.settings = self.getSettings()
        self.nickname = wx.TextCtrl(self.panels_connexion, 125, self.settings["NICKNAME"], size=(300,25), pos=(330,2))
        #self.channel_choices = ["#playonlinux-fr","#playonlinux-en","#playonlinux-it","#playonlinux-ru","#playonlinux-pl","#playonlinux-hu","#playonlinux-es"]
        #self.channel_choices.sort()
        #self.channel = wx.ComboBox(self.panels_connexion, 130,  _("Join a channel"), size=(190,28), pos=(510,0), choices=self.channel_choices)
        self.close.Enable(False)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizerInputs = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerMain = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer.Add(self.panels_connexion, 3, wx.EXPAND|wx.ALL, 2)
        self.sizer.Add(self.panels_main, 36, wx.EXPAND|wx.ALL, 2)
        self.sizer.Add(self.panels_button, 4, wx.EXPAND|wx.ALL, 2)

        self.sizerInputs.Add(self.field, 14, wx.EXPAND|wx.ALL, 2)
        self.sizerInputs.Add(self.button, 4, wx.EXPAND|wx.ALL, 2)

        self.sizerMain.Add(self.window, 4, wx.EXPAND|wx.ALL, 2)
        self.sizerMain.Add(self.content, 10, wx.EXPAND|wx.ALL, 2)
        self.sizerMain.Add(self.buddy, 4, wx.EXPAND|wx.ALL, 2)

        self.panel.SetSizer(self.sizer)
        self.panels_button.SetSizer(self.sizerInputs)
        self.panels_main.SetSizer(self.sizerMain)
        self.panel.SetAutoLayout(True)

        self.AddPage(self.panel, nom)
        self.field.Bind(wx.EVT_KEY_UP, self.EventKey)
        self.nickname.Bind(wx.EVT_KEY_UP, self.NicknameKey)
        #self.channel.Bind(wx.EVT_KEY_UP, self.EventChannel)

        wx.EVT_COMBOBOX(self, 130, self.JoinChan)
        wx.EVT_BUTTON(self,  122,  self.EventButton)
        wx.EVT_BUTTON(self,  123,  self.EventStart)
        wx.EVT_BUTTON(self,  124,  self.EventStop)
        wx.EVT_BUTTON(self,  128,  self.EventClose)
        wx.EVT_TREE_ITEM_ACTIVATED(self, 126, self.AddNick)
        #wx.EVT_TREE_ITEM_ACTIVATED(self, 127, self.filtrer)
        #self.disconnect.Enable(False)
        #self.EventStart(self)

    def AddNick(self, event):
        self.buddy_txt = self.buddy.GetItemText(self.buddy.GetSelection()).encode("utf-8","replace")
        irc.join(self.buddy_txt)
        #if(self.buddy_txt not in irc.chans):

        #self.field.SetValue("/msg "+self.buddy_txt+" ")
        #self.OpenWindow(self.buddy_txt)

    def SendMessage(self):
        self.chars = self.field.GetValue().replace('\n','').encode("utf-8","replace")
        if(self.chars):
            self.field.Clear()
            irc.SendMSG(self.chars)
        else:
            self.field.Clear()

    def EventClose(self, event):
        #index = irc.get_index(self.window.GetItemText(self.window.GetSelection()).lower()):
        #print index

        #del irc.messages[index]
        #del irc.names[index]
        #del irc.endnames[index]
        #del irc.chans[index]
        irc.leave_chan(self.window.GetItemText(self.window.GetSelection()).lower())

        self.window.Delete(self.window.GetSelection())
        #self.close.Enable(False)

    def EventStart(self, event):
        irc.Nick = self.nickname.GetValue().encode("utf-8","replace")
        irc.Connexion()

    def EventChannel(self, event):
        if(event.GetKeyCode() == wx.WXK_RETURN):
            self.JoinChan(self)

        event.Skip()

    def JoinChan(self, event):
        my_chan = self.channel.GetValue()
        if(my_chan[0] == "#"):
            if(irc.ircconnected == True):
                irc.join(my_chan)
        self.channel.SetValue(_("Join a channel"))
    def EventStop(self, event):
        irc.stop()

    def EventButton(self, event):
        self.SendMessage()

    def EventKey(self, event):
        if(event.GetKeyCode() == wx.WXK_RETURN):
            self.SendMessage()

        event.Skip()

    def NicknameKey(self, event):
        if(event.GetKeyCode() == wx.WXK_RETURN):
            if(irc.ircconnected == True):
                irc.ChangeNick(self.nickname.GetValue().encode("utf-8","replace"))
            else:
                irc.Connexion()
        event.Skip()


class IrcClient(wx.Frame):
    def __init__(self,parent,title=""):
        wx.Frame.__init__(self, parent, -1, title, size = (700, 500))

        self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.timer = wx.Timer(self, 1)
        self.onglets = Onglets(self)
        #self.onglets.hide()
        self.onglets.AjouteIRC(_("Messenger"))
        self.oldreload = ""
        self.oldimg = ""
        self.names = ["~"]
        self.messages = ["~"]
        self.chans = ["~"]
        self.already_connected = False
        self.settings = irc.getSettings()
        self.resized = False
        #self.settings["AUTOCONNECT"] = "TRUE"
        #Timer, regarde toute les secondes si il faut actualiser la liste
        self.Bind(wx.EVT_TIMER, self.AutoReload, self.timer)
        wx.EVT_CLOSE(self, self.CloseIRC)
        self.timer.Start(200)

    def CloseIRC(self, event):
        if(not irc.ircconnected or wx.YES == wx.MessageBox(_('If you close this window, you cannot read further replies. Are you sure that you want to close it?').format(os.environ["APPLICATION_TITLE"]).decode("utf-8","replace"), os.environ["APPLICATION_TITLE"] ,style=wx.YES_NO | wx.ICON_QUESTION)):
            self.onglets.EventStop(self)
            self.Destroy()

    def change_irc_window(self, event):
        #self.irc_user_list(self)
        self.html_reload(self)
        #print self.onglets.window.GetItemText(self.onglets.window.GetSelection())

    def irc_key(self, item):
        if(item[0] == "~"):
            return ("A")
        else:
            if(item[0] == "@" or item[0] == "&"):
                return ("B")
            else :
                if(item[0] == "%"):
                    return ("C")
                else:
                    if(item[0] == "+"):
                        return ("D")
                    else:
                        return string.lower(item[0])

    def html_reload(self, event):
                #print("Refresh html")
        self.window_txt = self.onglets.window.GetItemText(self.onglets.window.GetSelection()).encode("utf-8","replace")
        irc.selected_window = self.window_txt
        self.chat_content = ""
        # On regarde quelle liste on va prendre
        id_liste = irc.get_index(self.window_txt)
        # On ajoute tout
        self.i = 0
        if(len(irc.messages[id_liste]) >= 300):
            del irc.messages[id_liste][0]

        while(self.i < len(irc.messages[id_liste])):
            if(self.i != 0):
                self.chat_content += "\n<br />"
            self.chat_content += irc.messages[id_liste][self.i]
            self.i += 1
        self.onglets.content.SetPage("<html><head></head><body><p align='left'>"+self.chat_content+"</p></body></html>")
        self.onglets.content.Scroll(0,len(irc.messages[id_liste])*2)

    def html_reload_status(self, event):
        self.chat_content = ""
        # On regarde quelle liste on va prendre
        self.i = 0
        if(len(irc.status_messages) >= 300):
            del irc.status_messages[0]

        while(self.i < len(irc.status_messages)):
            self.chat_content += irc.status_messages[self.i]+"<br />\n"
            self.i += 1
        self.onglets.content.SetPage("<html><head></head><body><p align='left'>"+self.chat_content+"</p></body></html>")
        self.onglets.content.Scroll(0,len(irc.status_messages)*2)

    def irc_user_list(self, event):
        self.window_txt = self.onglets.window.GetItemText(self.onglets.window.GetSelection()).encode("utf-8","replace").lower()

        irc.selected_window = self.window_txt
        # On casse tout
        self.onglets.buddy.DeleteAllItems()
        self.buddy_root = self.onglets.buddy.AddRoot("")
        # On regarde quelle liste on va prendre
        id_liste = irc.get_index(self.window_txt)
        # On ajoute tout
        self.user_i = 0
        while(self.user_i < len(irc.names[id_liste])):
            num = 3
            irc.names[id_liste].sort(key=self.irc_key)
            if("@" in irc.names[id_liste][self.user_i] or "&" in irc.names[id_liste][self.user_i]):
                num = 0
            if("~" in irc.names[id_liste][self.user_i]):
                num = 4
            if("%" in irc.names[id_liste][self.user_i]):
                num = 1
            if("+" in irc.names[id_liste][self.user_i]):
                num = 2
            self.onglets.buddy.AppendItem(self.buddy_root, irc.names[id_liste][self.user_i].replace("&","").replace("~","").replace("%","").replace("+","").replace("@",""), num)
            html_hex = irc.GenColor(irc.names[id_liste][self.user_i].replace("&","").replace("~","").replace("%","").replace("+","").replace("@",""))
            self.couleur = [pow(int(html_hex[2],16),2),pow(int(html_hex[3],16),2),pow(int(html_hex[4],16),2)]
            self.onglets.buddy.SetItemTextColour(self.onglets.buddy.GetLastChild(self.buddy_root), wx.Colour(int(self.couleur[0]),int(self.couleur[1]),int(self.couleur[2])))
            self.user_i += 1
        #wx.Yield()

    def AutoReload(self, event):
        if(self.resized == False): # wx 2.9 resizing probem
            self.SetSize((800,500))
            self.resized = True

        self.new_string = irc.string_to_write
        if(irc.ircconnected == True):
            if(self.chans != irc.chans):
                self.onglets.OpenWindow()
                self.chans = irc.chans[:]
                #print "Refresh"
            #else :
            #print str(self.chans)+" --- "+str(irc.chans)

            self.window_txt = self.onglets.window.GetItemText(self.onglets.window.GetSelection()).encode("utf-8","replace").lower()

            if(len(self.window_txt) > 0):
                id_liste = irc.get_index(self.window_txt)
                if(self.window_txt[0] == "#"):
                #print self.names
                    if(irc.names[id_liste] != self.names):
                        self.irc_user_list(self)
                        self.names = irc.names[id_liste][:]

            #if(len(irc.messages) > id_liste+1):

                if(irc.messages[id_liste] != self.messages):
                    self.html_reload(self)
                    self.messages = irc.messages[id_liste][:]

            if(irc.select_window != ""):
                self.onglets.selectWindow(irc.select_window)
                irc.select_window = ""

            if(self.onglets.window.GetItemText(self.onglets.window.GetSelection()) != irc.selected_window):
                irc.selected_window = self.onglets.window.GetItemText(self.onglets.window.GetSelection())

            if(irc.selected_window == "#playonlinux" or irc.selected_window == ""):
                self.onglets.close.Enable(False)
            else:
                self.onglets.close.Enable(True)


            self.onglets.connect.Hide()
            self.onglets.disconnect.Show()
            if(len(self.chans) == 0):
                if(irc.status_messages != self.messages):
                    self.html_reload_status(self)
                    self.messages = irc.status_messages[:]
        else:
            if(irc.status_messages != self.messages):
                self.html_reload_status(self)
                self.messages = irc.status_messages[:]

            self.onglets.buddy.DeleteAllItems()
            self.onglets.window.DeleteAllItems()
            self.onglets.connect.Show()
            self.onglets.disconnect.Hide()
            if(self.settings["AUTOCONNECT"] == "1"):
                if(self.already_connected == False):
                    irc.Nick = self.onglets.nickname.GetValue().encode("utf-8","replace")
                    irc.connect()
                    self.already_connected = True;





irc = irc.IRCClient()
