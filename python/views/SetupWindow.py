#!/usr/bin/python
# -*- coding:Utf-8 -*-

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



import wx, wx.animate, os, getopt, sys, urllib, signal, time, string, urlparse, codecs, time, threading, socket
from subprocess import Popen,PIPE

from lib.Context import Context
from lib.UIHelper import UIHelper
from lib.GuiServer import GuiServer
from lib.Downloader import Downloader


class SetupWindow(wx.Frame): #fenêtre principale
    def __init__(self, title, scriptPid, topImage, leftImage, isProtected):
        
        
        wx.Frame.__init__(self, None, -1, title, style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX, size = (520, 398 + UIHelper().addWindowMacOffset()))
        self.SetIcon(wx.Icon(Context().getAppPath()+"/resources/icons/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.Center(wx.BOTH)
        self.Show(True)
        
        self.bashPid = scriptPid
        self.protectedWindow = isProtected
        
        
        
        if(os.path.exists(topImage)):
            self.topImage = wx.Bitmap(topImage)
        else:
            self.topImage = wx.Bitmap(Context().getAppPath()+"/resources/images/setups/default/top.png")
        
        if(os.path.exists(leftImage)):
            self.leftImage = wx.Bitmap(topImage)
        else:
            if(Context().getOS() == "Linux"):
                self.leftImage = wx.Bitmap(Context().getAppPath()+"/resources/images/setups/default/playonlinux.jpg")
            else:
                self.leftImage = wx.Bitmap(Context().getAppPath()+"/resources/images/setups/default/playonmac.jpg")
            
                
       

        
        self.drawGUI()

        wx.EVT_CLOSE(self, self.Cancel)

    def drawGUI(self):
        # GUI elements
        self.panel = wx.Panel(self, -1, pos=(0,0), size=((520, 398 + UIHelper().addWindowMacOffset())))
        self.header = wx.Panel(self.panel, -1, style = UIHelper().widgetBorders(), size=(522,65))
        self.header.SetBackgroundColour((255,255,255))
        self.footer = wx.Panel(self.panel, -1, size=(522,45), pos=(-1,358), style = UIHelper().widgetBorders())

        # Panels
        self.MainPanel = wx.Panel(self.panel, -1, pos=(150,0), size=(370,356))
        self.MainPanel.SetBackgroundColour((255,255,255))


        # Images
        self.topImageWidget = wx.StaticBitmap(self.header, -1, self.topImage, (520 - self.topImage.GetWidth() , 0), wx.DefaultSize)
        self.leftImageWidget = wx.StaticBitmap(self.panel, -1, self.leftImage, (0,0), wx.DefaultSize)


        # Text
        titreHeader = wx.StaticText(self.header, -1, _('{0} Wizard').format(Context().getAppName()),pos=(5,5), size=(340,356),style=wx.ST_NO_AUTORESIZE)
        titreHeader.SetFont(UIHelper().getFontTitle())
        titreHeader.SetForegroundColour((0,0,0)) # For dark themes

        self.texte = wx.StaticText(self.panel, -1, "",pos=(20,80),size=(480,275),style=wx.ST_NO_AUTORESIZE)
        self.texte_bis = wx.StaticText(self.panel, -1, "",size=(480,30),style=wx.ST_NO_AUTORESIZE)
        self.titre = wx.StaticText(self.header, -1, "",pos=(20,30), size=(340,356),style=wx.ST_NO_AUTORESIZE)
        self.titre.SetForegroundColour((0,0,0)) # For dark themes

        self.texteP = wx.StaticText(self.MainPanel, -1, "",pos=(5,50))
        self.texteP.SetForegroundColour((0,0,0)) # For dark themes

        self.titreP = wx.StaticText(self.MainPanel, -1,"",pos=(5,5), size=(340,356))
        self.titreP.SetFont(UIHelper().getFontTitle())
        self.titreP.SetForegroundColour((0,0,0)) # For dark themes

        self.txtEstimation = wx.StaticText(self.panel, -1, "",size=(480,30),style=wx.ST_NO_AUTORESIZE)
        self.register_link = ""


        # Buttons
        self.CancelButton = wx.Button(self.footer, wx.ID_CANCEL, _("Cancel"), pos=(430,0),size=(85,37))
        if(self.protectedWindow == True):
            self.CancelButton.Enable(False)

        self.NextButton = wx.Button(self.footer, wx.ID_FORWARD, _("Next"), pos=(340,0),size=(85,37))
        self.BackButton = wx.Button(self.footer, wx.ID_FORWARD, _("Back"), pos=(250,0),size=(85,37))
        self.InfoScript = wx.StaticBitmap(self.footer, -1, wx.Bitmap(Context().getAppPath()+"/resources/images/setups/about.png"), pos=(10,8))
        self.InfoScript.Hide()
        self.script_ID = 0
        self.InfoScript.Bind(wx.EVT_LEFT_DOWN, self.InfoClick)
        self.InfoScript.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        self.NoButton = wx.Button(self.footer, wx.ID_NO, _("No"), pos=(430,0),size=(85,37))
        self.YesButton = wx.Button(self.footer, wx.ID_YES, _("Yes"), pos=(340,0), size=(85,37))
        self.browse = wx.Button(self.panel, 103, _("Browse"), size=(130,40))
        self.browse_text = wx.StaticText(self.panel, -1, "")
        self.browse_image = wx.StaticBitmap(self.panel, -1, wx.Bitmap(Context().getAppPath()+"/etc/playonlinux.png"))

        # D'autres trucs
        self.champ = wx.TextCtrl(self.panel, 400, "",size=(300,22))

        self.bigchamp = wx.TextCtrl(self.panel, -1, "",size=wx.Size(460,240), pos=(30,105),style = UIHelper().widgetBorders()|wx.TE_MULTILINE)
        self.MCheckBox = wx.CheckBox(self.panel, 302, _("I Agree"), pos=(20,325))
        self.PCheckBox = wx.CheckBox(self.panel, 304, _("Show virtual drives"), pos=(20,325))
        self.Menu = wx.ListBox(self.panel, 104, pos=(25,105),size=(460,220), style = UIHelper().widgetBorders())
        self.scrolled_panel = wx.ScrolledWindow(self.panel, -1, pos=(20,100), size=(460,220), style= UIHelper().widgetBorders()|wx.HSCROLL|wx.VSCROLL)
        self.scrolled_panel.SetBackgroundColour((255,255,255))
        self.texte_panel = wx.StaticText(self.scrolled_panel, -1, "",pos=(5,5))

        self.gauge = wx.Gauge(self.panel, -1, 50, size=(375, 20))
        self.WaitButton = wx.Button(self.panel, 310, "", size=(250,25))

        
        
        self.animation = wx.StaticBitmap(self.panel, -1, self.getLoaderFromAngle(1), (228,170))
        self.current_angle = 1
    
        self.images = wx.ImageList(22, 22)
        self.MenuGames = wx.TreeCtrl(self.panel, 111, style=wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT|UIHelper().widgetBorders(), pos=(25,105),size=(460,220))
        self.MenuGames.SetImageList(self.images)
        self.MenuGames.SetSpacing(0)
        

        # Login
        self.login = wx.StaticText(self.panel, -1, _("Login: "),pos=(20,120),size=(460,20))
        self.password = wx.StaticText(self.panel, -1, _("Password: "),pos=(20,150),size=(460,20))
        self.loginbox =  wx.TextCtrl(self.panel, -1, "",size=(250,22),pos=(200,115))
        self.passbox =  wx.TextCtrl(self.panel, -1, "",size=(250,22),pos=(200,145), style=wx.TE_PASSWORD)
        self.register = wx.HyperlinkCtrl(self.panel, 303, _("Register"), "", pos=(20,180))
        self.register.SetNormalColour(wx.Colour(0,0,0))

        # Fixed Events
        wx.EVT_BUTTON(self, wx.ID_YES, self.release_yes)
        wx.EVT_BUTTON(self, wx.ID_NO, self.release_no)
        wx.EVT_BUTTON(self, wx.ID_CANCEL , self.Cancel)
        wx.EVT_BUTTON(self, 103, self.Parcourir)
        wx.EVT_CHECKBOX(self, 302, self.agree)
        wx.EVT_CHECKBOX(self, 304, self.switch_menu)
        wx.EVT_HYPERLINK(self, 303, self.POL_register)

        # Debug Window
        self.debugImage = wx.StaticBitmap(self.panel, -1, wx.Bitmap(Context().getAppPath()+"/resources/images/setups/face-sad.png"), (196,130))
        self.debugZone = wx.TextCtrl(self.panel, -1, "",size=wx.Size(440,82), pos=(40,274),style=UIHelper().widgetBorders()|wx.TE_MULTILINE|wx.TE_READONLY)

        # Hide all
        self.hideAll()
        self.animation.Show()
        self.footer.Hide()
        
        # Set the timer
        self.timer = wx.Timer(self, 3)
        self.Bind(wx.EVT_TIMER, self.timerAction, self.timer)
        self.timer.Start(100)
        self.timerDownload = False
        self.timerAnimate = True
        
    def getLoaderFromAngle(self, angle):
        if(angle >= 1 and angle <= 12):
            image = wx.Image(Context().getAppPath()+"/resources/images/setups/wait/"+str(angle)+".png")
        return image.ConvertToBitmap()
        
    def hideAll(self):
        self.footer.Show()
        self.header.Hide()
        self.leftImageWidget.Hide()
        self.CancelButton.Hide()
        self.MainPanel.Hide()
        self.NextButton.Hide()
        self.BackButton.Hide()
        self.NoButton.Hide()
        self.YesButton.Hide()
        self.browse.Hide()
        self.browse_text.Hide()
        self.browse_image.Hide()
        self.champ.Hide()
        self.bigchamp.Hide()
        self.texte.Hide()
        self.texte_bis.Hide()
        self.texteP.Hide()
        self.titre.Hide()
        self.Menu.Hide()
        self.MenuGames.Hide()
        self.scrolled_panel.Hide()
        self.gauge.Hide()
        self.txtEstimation.Hide()
        self.texte_panel.Hide()
        self.MCheckBox.Hide()
        self.PCheckBox.Hide()
        self.NextButton.Enable(True)
        self.login.Hide()
        self.loginbox.Hide()
        self.password.Hide()
        self.passbox.Hide()
        self.register.Hide()
        self.WaitButton.Hide()
        self.MCheckBox.SetValue(False)
        self.PCheckBox.SetValue(False)
        self.animation.Hide()
        self.timerAnimate = False
        self.debugImage.Hide()
        self.debugZone.Hide()
        self.Refresh()

                
    def timerAction(self, event):
        ## If the setup window is downloading a file, we need to update the progress bar
        if(self.timerDownload == True):
            if(self.downloader.taille_bloc != 0):
                self.gauge.SetRange(self.downloader.getMaxNbBlock())
                self.gauge.SetValue(self.downloader.getNbBlocks())

                tailleFichierN = str(round(self.downloader.getFileSizeInBytes(), 1))
                octetsLoadedN = str(round(self.downloader.getLoadedSizeInBytes(), 1))

                self.txtEstimation.SetLabel(_("{0} of {1} MB downloaded").format(octetsLoadedN, tailleFichierN))

            if(self.downloader.isFinished()):
                if(self.downloader.hasFailed()):
                    self.release_but_fail(self)
                else:
                    self.release(self)
                    
                self.timerDownload = False

        if(self.timerAnimate == True):
            self.current_angle = ((self.current_angle + 1) % 12)
            self.animation.SetBitmap(self.getLoaderFromAngle(self.current_angle + 1))
            
    ### Theses methods command the window. There are called by mainWindow when it reads the queue
    def POL_SetupWindow_message(self, message, title):
        self.hideAll()
        self.DrawDefault(message, title)

        self.DrawCancel()
        self.DrawNext()
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release)

    def POL_SetupWindow_free_presentation(self, title, message):
        self.hideAll()
        self.MainPanel.Show()
        self.titreP.SetLabel(title.decode("utf8","replace"))
        self.titreP.Wrap(280)

        self.texteP.SetLabel(message.decode("utf8","replace").replace("\\n","\n").replace("\\t","\t"))
        self.texteP.Wrap(360)
        self.texteP.Show()

        self.DrawCancel()
        self.DrawNext()

        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release)
        self.DrawImage()
    
    def POL_SetupWindow_SetID(self, script_id):
        self.InfoScript.Show()
        self.script_ID = script_id

    def POL_SetupWindow_UnsetID(self):
        self.InfoScript.Hide()

    def InfoClick(self, e):
        url = "http://www.playonlinux.com/en/app-"+self.script_ID+".html"
        if(Context().getOS() == "Mac"):
            os.system("open "+url+" &")
        else:
            os.system("xdg-open "+url+" &")


    def POL_SetupWindow_textbox(self, message, title, value):
        self.hideAll()
        self.DrawDefault(message, title)

        self.space = message.count("\\n")+1

        self.champ.SetPosition((20,85+self.space*16))
        self.champ.SetValue(value)
        self.champ.Show()

        self.DrawCancel()
        self.DrawNext()
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_champ)
        wx.EVT_TEXT_ENTER(self, 400, self.release_champ)

    def POL_SetupWindow_debug(self, message, title, value):
        self.POL_SetupWindow_message(message, title)
        self.debugImage.Show()
        self.debugZone.Show()
        self.debugZone.SetValue(value.replace("\\n","\n"))

    def POL_SetupWindow_Pulse(self, value):
        self.gauge.SetValue(int(value)/2)
        self.SendBash()

    def POL_SetupWindow_PulseText(self, value):
        self.texte_bis.SetLabel(value.replace("\\n","\n"))
        self.texte_bis.SetPosition((20,135+self.space*16))
        self.texte_bis.Show()
        self.SendBash()

    def POL_SetupWindow_download(self, message, title, url, localfile): 
        self.hideAll()
        self.DrawDefault(message, title)
        self.space = message.count("\\n")+1
        self.gauge.Show()
        self.gauge.SetPosition((70,95+self.space*16))
        self.txtEstimation.SetPosition((20,135+self.space*16))
        self.txtEstimation.Show()
        self.DrawCancel()
        self.DrawNext()
        self.NextButton.Enable(False)
        self.downloadFile(url, localfile)

    def POL_SetupWindow_wait(self, message, title):
        self.hideAll()
        self.DrawDefault(message, title)
        self.NextButton.Enable(False)
        self.animation.Show()
        self.timerAnimate = True
        self.DrawCancel()
        self.DrawNext()
        self.NextButton.Enable(False)
        self.SendBash()

    def POL_SetupWindow_pulsebar(self, message, title):
        self.hideAll()
        self.DrawDefault(message, title)

        self.NextButton.Enable(False)
        
        self.space = message.count("\\n")+1
        self.gauge.SetPosition((70,95+self.space*16))
        self.gauge.Show()
        
        self.DrawCancel()
        self.DrawNext()
        self.NextButton.Enable(False)
        self.SendBash()
        
    def POL_SetupWindow_wait_b(self, message, title, button_value, command, alert):
        self.POL_SetupWindow_wait(message, title)    
        self.WaitButton.Show()
        self.WaitButton.SetLabel(button_value) 
        self.space = message.count("\\n")+1
        self.WaitButton.SetPosition((135,115+self.space*16))
        self.Bind(wx.EVT_BUTTON, lambda event:
            self.RunCommand(event,command,alert),self.WaitButton)

    def POL_SetupWindow_question(self, message, title):
        self.hideAll()
        self.DrawDefault(message, title)

        self.YesButton.Show()
        self.NoButton.Show()

    def POL_SetupWindow_menu(self, message, title, liste, cut, numtype=False):
        self.hideAll()
        self.DrawDefault(message, title)

        self.space = message.count("\\n")+1
        self.areaList = string.split(liste,cut)

        self.Menu.SetPosition((20,85+self.space*16))

        self.Menu.Clear()
        self.Menu.InsertItems(self.areaList,0)
        self.Menu.Select(0)
        self.Menu.Show()

        self.DrawCancel()
        self.DrawNext()

        if(numtype == False):
            wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_menu)
            wx.EVT_LISTBOX_DCLICK(self, 104, self.release_menu)
        else:
            wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_menu_num)
            wx.EVT_LISTBOX_DCLICK(self, 104, self.release_menu_num)

    def POL_SetupWindow_browse(self, message, title, value, directory, supportedfiles):
        self.POL_SetupWindow_textbox(message, title, value)
        self.supportedfiles = supportedfiles
        self.champ.Hide()
        self.directory = directory
        self.browse.SetPosition((195,130))
        self.browse.Show()
        self.NextButton.Enable(False)


    def POL_SetupWindow_login(self, message, title, register_url):
        self.hideAll()
        self.DrawDefault(message, title)

        self.space = message.count("\\n")+1
        self.register_link = register_url

        self.login.Show()
        self.loginbox.Show()
        self.password.Show()
        self.passbox.Show()
        self.register.Show()

        self.DrawCancel()
        self.DrawNext()

        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_login)

    def POL_SetupWindow_textbox_multiline(self, message, title, value):
        self.hideAll()
        self.DrawDefault(message, title)
        self.space = message.count("\\n")+1

        self.bigchamp.SetPosition((20,85+self.space*16))
        self.bigchamp.SetValue(value)

        self.bigchamp.Show()

        self.DrawCancel()
        self.DrawNext()
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_bigchamp)

    def POL_SetupWindow_checkbox_list(self, message, title, liste, cut):
        self.hideAll()
        self.DrawDefault(message, title)

        self.scrolled_panel.Show()
        self.space = message.count("\\n")+1

        self.scrolled_panel.SetPosition((20,85+self.space*16))
        self.areaList = string.split(liste,cut)

        # We have to destroy all previous items (catching exception in case one is already destroyed)
        self.i = 0
        try:
            while(self.i <= len(self.item_check)):
                self.item_check[self.i].Destroy()
                self.i+=1
        except:
            pass
        self.item_check = []

        # Now we can rebuild safely the widget
        self.i = 0
        while(self.i < len(self.areaList)):
            self.item_check.append(wx.CheckBox(self.scrolled_panel, -1, pos=(0,(self.i*25)),label=str(self.areaList[self.i])))
            self.i+=1

        self.scrolled_panel.SetVirtualSize((0,self.i*(25)))
        self.scrolled_panel.SetScrollRate(0,25)
        self.DrawCancel()
        self.DrawNext()
        self.separator = cut
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_checkboxes)


    def POL_SetupWindow_shortcut_list(self, message, title):
        self.hideAll()
        self.DrawDefault(message, title)

        self.add_games()

        self.space = message.count("\\n")+1
        self.MenuGames.SetPosition((20,85+self.space*16))
        self.MenuGames.Show()

        self.DrawCancel()
        self.DrawNext()
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_menugame)
        wx.EVT_TREE_ITEM_ACTIVATED(self, 111, self.release_menugame)

    def POL_SetupWindow_icon_menu(self, message, title, items, cut, icon_folder, icon_list):
        self.hideAll()
        self.DrawDefault(message, title)

        self.add_menu_icons(items, cut, icon_list, icon_folder);

        self.space = message.count("\\n")+1
        self.MenuGames.SetPosition((20,85+self.space*16))
        self.MenuGames.Show()

        self.DrawCancel()
        self.DrawNext()
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_menugame)
        wx.EVT_TREE_ITEM_ACTIVATED(self, 111, self.release_menugame)

    def POL_SetupWindow_prefix_selector(self, message, title):
        self.hideAll()
        self.DrawDefault(message, title)

        self.add_games()
        self.MenuGames.Show()

        self.space = message.count("\\n")+1
        self.Menu.SetPosition((20,85+self.space*16))
        self.Menu.Clear()

        self.areaList = os.listdir(Context().getUserRoot()+"/wineprefix/")
        self.areaList.sort()

        for file in self.areaList:
            if (str(file[0]) == "."):
                self.areaList.remove(file)

        self.Menu.InsertItems(self.areaList,0)
        self.Menu.Select(0)
        self.Menu.Hide()

        self.DrawCancel()
        self.DrawNext()

        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release_menuprefixes)
        wx.EVT_TREE_ITEM_ACTIVATED(self, 111, self.release_menuprefixes)
        wx.EVT_LISTBOX_DCLICK(self, 104, self.release_menuprefixes)

        self.PCheckBox.Show()


    def POL_SetupWindow_licence(self, message, title, licence_file):
        self.hideAll()
        self.DrawDefault(message, title)

        try:
            self.texte_panel.SetLabel(open(licence_file,"r").read())
        except:
            self.texte_panel.SetLabel("E. file not found :"+licence_file)

        self.texte_panel.Wrap(400)
        self.texte_panel.Show()

        self.scrolled_panel.Show()
        self.scrolled_panel.SetVirtualSize(self.texte_panel.GetSize())
        self.scrolled_panel.SetScrollRate(0,25)

        self.MCheckBox.Show()

        self.DrawCancel()
        self.DrawNext()
        self.NextButton.Enable(False)
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release)


    def POL_SetupWindow_file(self, message, title, filetoread):
        self.hideAll()
        self.DrawDefault(message, title)

        try:
            self.texte_panel.SetLabel(open(filetoread,"r").read())
        except:
            self.texte_panel.SetLabel("E. File not found")
            
        self.texte_panel.Wrap(400)
        self.texte_panel.Show()

        self.scrolled_panel.Show()
        self.scrolled_panel.SetVirtualSize(self.texte_panel.GetSize())
        self.scrolled_panel.SetScrollRate(0,25)

        self.DrawCancel()
        self.DrawNext()
        wx.EVT_BUTTON(self, wx.ID_FORWARD, self.release)




    def POL_register(self, event):
        if(Context().getOS() == "Mac"):
            os.system("open "+self.register_link)
        else:
            os.system("xdg-open "+self.register_link)

    def RunCommand(self, event, command,confirm):
        if(confirm == "0" or wx.YES == wx.MessageBox(confirm.decode("utf-8","replace"), Context().getAppName(), style=wx.YES_NO | wx.ICON_QUESTION)):
            os.system(command+"&");

    def DrawImage(self):
        self.leftImageWidget.Show()

    def DrawHeader(self):
        self.header.Show()


    def DrawDefault(self, message, title):
        self.DrawHeader()
        self.texte.SetLabel(message.replace("\\n","\n").replace("\\t","\t"))
        self.texte.Show()
        self.titre.SetLabel(title)
        self.titre.Show()

    def DrawCancel(self):
        self.CancelButton.Show()

    def DrawNext(self):
        self.NextButton.Show()

    def SendBash(self, var=""):
        GuiServer().getState().set(self.bashPid, var)

    def release(self, event):
        self.SendBash()
        self.NextButton.Enable(False)

    def release_but_fail(self, event):
        self.SendBash("Fail")
        self.NextButton.Enable(False)

    def release_checkboxes(self, event):
        i = 0
        send = []
        while(i < len(self.item_check)):
            if(self.item_check[i].IsChecked() == True):
                send.append(self.areaList[i])
            i += 1
        self.SendBash(string.join(send,self.separator))
        self.NextButton.Enable(False)

    def release_yes(self, event):
        self.SendBash("TRUE")
        self.NextButton.Enable(False)

    def release_no(self, event):
        self.SendBash("FALSE")
        self.NextButton.Enable(False)

    def release_login(self, event):
        self.SendBash(self.loginbox.GetValue().encode("utf-8","replace")+"~"+self.passbox.GetValue().encode("utf-8","replace"))
        self.NextButton.Enable(False)

    def release_champ(self, event):
        self.SendBash(self.champ.GetValue().encode("utf-8","replace"))
        self.NextButton.Enable(False)

    def release_bigchamp(self, event):
        self.SendBash(self.bigchamp.GetValue().replace("\n","\\n").encode("utf-8","replace"))
        self.NextButton.Enable(False)

    def release_menu(self,event):
        self.SendBash(self.areaList[self.Menu.GetSelection()])
        self.NextButton.Enable(False)

    def release_menu_num(self,event):
        self.SendBash(str(self.Menu.GetSelection()))
        self.NextButton.Enable(False)

    def release_icons(self,event):
        if(self.menu.IsChecked()):
            self.SendBash("MSG_MENU=True")
        if(self.desktop.IsChecked()):
            self.SendBash("MSG_DESKTOP=True")
        if(self.desktop.IsChecked() and self.menu.IsChecked()):
            self.SendBash("MSG_DESKTOP=True\nMSG_MENU=True")
        if(self.desktop.IsChecked() == False and self.menu.IsChecked() == False):
            self.SendBash("Ok")
        self.NextButton.Enable(False)

    def release_menugame(self,event):     
        self.SendBash(self.MenuGames.GetItemText(self.MenuGames.GetSelection()).encode("utf-8","replace"))
        self.NextButton.Enable(False)

    def release_menuprefixes(self,event):
        if(self.PCheckBox.IsChecked() == False): # Alors il faut renvoyer le prefix
            self.SendBash("1~"+self.MenuGames.GetItemText(self.MenuGames.GetSelection()).encode("utf-8","replace"))
        else:
            self.SendBash("2~"+self.areaList[self.Menu.GetSelection()])

        self.NextButton.Enable(False)

    def Cancel(self, event):
        if(self.protectedWindow == False):
            self.Destroy()
            time.sleep(0.1)
            os.system("kill -9 -"+self.bashPid+" 2> /dev/null")
            os.system("kill -9 "+self.bashPid+" 2> /dev/null") 
        else:
            wx.MessageBox(_("You cannot close this window").format(Context().getAppName()),_("Error"))

    def add_games(self):
        apps = os.listdir(Context().getUserRoot()+"/shortcuts/")
        apps.sort()
        self.images.RemoveAll()
        self.MenuGames.DeleteAllItems()
        self.root = self.MenuGames.AddRoot("")
        i = 0
        for app in apps:
            appfile = Context().getUserRoot()+"/shortcuts/"+app
            if(not os.path.isdir(appfile)):
                fichier = open(appfile,"r").read()

                if("POL_Wine " in fichier):
                    if(os.path.exists(Context().getUserRoot()+"/icones/32/"+app)):
                        file_icon = Context().getUserRoot()+"/icones/32/"+app
                    else:
                        file_icon = Context().getAppPath()+"/etc/playonlinux32.png"

                    bitmap = wx.Image(file_icon)
                    bitmap.Rescale(22,22,wx.IMAGE_QUALITY_HIGH)
                    bitmap = bitmap.ConvertToBitmap()
                    self.images.Add(bitmap)
                    self.MenuGames.AppendItem(self.root, app, i)
                    i += 1


    def add_menu_icons(self, items, cut, icon_list, icon_folder):
        elements = items.split(cut)
        icons = icon_list.split(cut)
        
        #self.games.sort()
        self.images.RemoveAll()
        self.MenuGames.DeleteAllItems()
        self.root = self.MenuGames.AddRoot("")
        i = 0
        for index in elements:
            current_icon = icon_folder+"/"+icons[i]
            if(os.path.exists(current_icon)):
                file_icon = current_icon
            else:
                file_icon = Context().getAppPath()+"/ressources/icons/playonlinux32.png"

            bitmap = wx.Image(file_icon)
            bitmap.Rescale(22,22,wx.IMAGE_QUALITY_HIGH)
            bitmap = bitmap.ConvertToBitmap()
            self.images.Add(bitmap)
            self.MenuGames.AppendItem(self.root, index, i)
            i+=1



    def Parcourir(self, event):
        if(self.supportedfiles == "All"):
            self.FileDialog = wx.FileDialog(self.panel)
        else:
            self.FileDialog = wx.FileDialog(self.panel, wildcard=self.supportedfiles)
        self.FileDialog.SetDirectory(self.directory)
        self.FileDialog.ShowModal()
        if(self.FileDialog.GetPath() != ""):
            filePath = self.FileDialog.GetPath().encode("utf-8","replace")
            filePathBaseName = filePath.split("/")[filePath.count("/")]
            self.champ.SetValue(filePath) 
            self.NextButton.Enable(True)
            self.browse_text.Show()
            self.browse_text.SetLabel(filePathBaseName)
            self.browse_text.SetPosition(((520-self.browse_text.GetSize()[0])/2,180))
            
            if(".exe" in filePathBaseName and os.path.getsize(filePath) <= 30*1024*1024):
                try:
                    tmpPath = Context().getUserRoot()+"/tmp/browse"+self.bashPid+".png"
                    try: os.path.remove(tmpPath)
                    except: pass
                    playonlinux.POL_System("POL_ExtractBiggestIcon \""+filePath+"\" "+tmpPath)
                    if(os.path.exists(tmpPath)):
                        browse_image = wx.Image(tmpPath)
                    else:
                        browse_image = wx.Image(Context().getAppPath()+"/etc/playonlinux.png")
                except:
                    browse_image = wx.Image(Context().getAppPath()+"/etc/playonlinux.png")
            else:
                browse_image = wx.Image(Context().getAppPath()+"/etc/playonlinux.png")
            
            if(browse_image.GetWidth() >= 48):
                browse_image.Rescale(48,48,wx.IMAGE_QUALITY_HIGH)
            browse_image = browse_image.ConvertToBitmap()
    
            self.browse_image.SetBitmap(browse_image)
            self.browse_image.SetPosition(((520-self.browse_image.GetSize()[0])/2,220))
            self.browse_image.Show()

        self.FileDialog.Destroy()


    def downloadFile(self, url, localB):   
        self.chemin = urlparse.urlsplit(url)[2]
        self.nomFichier = self.chemin.split('/')[-1]
        self.local = localB + self.nomFichier
        self.downloader = Downloader(url, self.local)
        self.downloader.start()
        self.timerDownload = True


    def agree(self, event):
        if(self.MCheckBox.IsChecked()):
            self.NextButton.Enable(True)
        else:
            self.NextButton.Enable(False)

    def switch_menu(self, event):
        if(self.PCheckBox.IsChecked()):
            self.Menu.Show()
            self.MenuGames.Hide()
        else:
            self.MenuGames.Show()
            self.Menu.Hide()
        self.Refresh()

