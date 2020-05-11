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
import subprocess

import wx

import lib.Variables as Variables
import lib.playonlinux as playonlinux


# from subprocess import Popen,PIPE

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title,logcheck="/dev/null",logtype=None):
        self.logtype = 1
        self.logfile = None
        self.logname = ""
        self.need_redisplay = False

        wx.Frame.__init__(self, parent, -1, title, size = (810, 600+Variables.windows_add_size), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)
        self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.SetTitle(_('{0} debugger').format(os.environ["APPLICATION_TITLE"]))
        #self.panelFenp = wx.Panel(self, -1)

        self.prefixes_item = {}
        self.logs_item = {}

        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER)
        self.panelEmpty = wx.Panel(self.splitter, -1)
        self.panelNotEmpty = wx.Panel(self.splitter, -1)


        self.noselect = wx.StaticText(self.panelEmpty, -1, _('Please select a debug file'),pos=(0,150),style=wx.ALIGN_RIGHT)
        self.noselect.SetPosition(((570-self.noselect.GetSize()[0])/2,250))
        self.noselect.Wrap(500)


        self.images = wx.ImageList(16, 16)

        self.list_game = wx.TreeCtrl(self.splitter, 900, size = wx.DefaultSize, style=wx.TR_HIDE_ROOT)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.analyseLog, id=900)


        self.list_game.SetSpacing(0);
        self.list_game.SetImageList(self.images)


        self.list_software()

        self.throttling = False
        self.line_buffer = ""
        self.timer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.AutoReload, self.timer)
        self.AutoReload(self)
        self.timer.Start(10)
        self.logfile = ""

        # Debug control
        self.panelText = wx.Panel(self.panelNotEmpty, -1, size=(590,500), pos=(2,2)) # Hack, wxpython bug
        self.log_reader = wx.TextCtrl(self.panelText, 100, "", size=wx.Size(590,500), pos=(2,2), style=Variables.widget_borders|wx.TE_RICH2|wx.TE_READONLY|wx.TE_MULTILINE)
        self.log_reader.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.openTextEdit = wx.Button(self.panelNotEmpty, 101, _("Locate this logfile"), size=(400,30), pos=(70,512))
        self.reportProblem = wx.Button(self.panelNotEmpty, 102, "", size=(400,30), pos=(70,552))

        if(logcheck == "/dev/null"):
            self.HideLogFile()
        else:
            self.analyseReal(logtype,logcheck)
        self.Bind(wx.EVT_BUTTON,self.locate,id=101)
        self.Bind(wx.EVT_BUTTON,self.bugReport,id=102)
        self.Bind(wx.EVT_CLOSE,self.app_Close)

        #self.log_reader.SetDefaultStyle(wx.TextAttr(font=wx.Font(13,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)))

    def bugReport(self, event):
        new_env = os.environ
        new_env["LOGTITLE"] = self.logname
        subprocess.Popen(["bash", Variables.playonlinux_env+"/bash/bug_report"], env=new_env)
        self.reportProblem.Enable(False)

    def locate(self, event):
        if(self.logtype == 0):
            dirname = Variables.playonlinux_rep+"wineprefix/"+self.logname+"/"
            filename = 'playonlinux.log'
        if(self.logtype == 1):
            dirname = Variables.playonlinux_rep+"logs/"+self.logname+"/"
            filename = self.logname+".log"
        wx.MessageBox(_("The file is named : {0}").format(filename), os.environ["APPLICATION_TITLE"])

        playonlinux.POL_Open(dirname)

    def ShowLogFile(self):
        self.splitter.Unsplit()
        self.splitter.SplitVertically(self.list_game,self.panelNotEmpty)
        self.splitter.SetSashPosition(200)

    def HideLogFile(self):
        self.splitter.Unsplit()
        self.splitter.SplitVertically(self.list_game,self.panelEmpty)
        self.splitter.SetSashPosition(200)

    def AppendStyledText(self, line):
        ins = self.log_reader.GetInsertionPoint()
        leng = len(line)
        if(leng > 200):
            line=line[0:200]
            leng=200

        self.log_reader.AppendText(line)

        self.bold = wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)

        try:
            if(line[0:5] == "wine:"):
                self.log_reader.SetStyle(ins, ins+5, wx.TextAttr("red", wx.NullColour))
            elif(line[0:6] == "fixme:"):
                self.log_reader.SetStyle(ins, ins+leng, wx.TextAttr(wx.Colour(100,100,100), wx.NullColour))
            elif(self.logtype == 1 and leng > 19 and line[17:20] == " - "):
                self.log_reader.SetStyle(ins, ins+17, wx.TextAttr("black", wx.NullColour, self.bold))
            elif(self.logtype == 0 and leng > 21 and line[19:22] == " - "):
                self.log_reader.SetStyle(ins, ins+19, wx.TextAttr("black", wx.NullColour, self.bold))
            else:
                self.log_reader.SetStyle(ins, ins+leng, wx.TextAttr("black", wx.NullColour))
        except wx._core.PyAssertionError:
            pass

    def AutoReload(self, event):
        if(self.logfile != "" and self.logfile != None):
            # Max number of lines to display per reload
            # Would be better if adjusted to effective display capability
            max_lines = 20

            circular_buffer = [u'' for i in range(max_lines)]
            index = 0
            # Did we overwrote lines in the circular buffer?
            wrapped_buffer = False
            overwritten_lines = 0

            while True:
                line = self.logfile.readline()
                if not line:
                    # Reached the current bottom of log, disable throttling
                    # Could mean we never disable it if we're overflowed with logs 
                    # from the very beginning
                    self.throttling = True
                    if self.log_reader.IsFrozen():
                        self.log_reader.Thaw()
                    break

                # Line buffering
                self.line_buffer += line
                if line[-1] != '\n':
                    break
                circular_buffer[index] = self.line_buffer
                self.line_buffer = ""

                index += 1
                if wrapped_buffer:
                    overwritten_lines += 1

                # Buffer wrapping
                if index >= max_lines:
                    if not self.throttling:
                        break
                    index = 0
                    wrapped_buffer = True

            if wrapped_buffer:
                if overwritten_lines > 0:
                    self.AppendStyledText("...skipped %d line(s)...\n" % overwritten_lines)
                    # Fix skipped line as soon as we have some free time
                    self.need_redisplay = True
                for k in range(index, max_lines):
                    self.AppendStyledText(circular_buffer[k])
            for k in range(0, index):
                self.AppendStyledText(circular_buffer[k])

    def OnFocus(self, event):
        if self.need_redisplay:
            print('Need to redisplay log')
            self.initLogDisplay()

    def analyseLog(self, event):
        parent =  self.list_game.GetItemText(self.list_game.GetItemParent(self.list_game.GetSelection()))
        selection =  self.list_game.GetItemText(self.list_game.GetSelection())
        if(parent == _("Virtual drives")):
            parent = 0
        else:
            parent = 1
        self.analyseReal(parent, selection)

    def analyseReal(self, parent, selection):
        self.ShowLogFile()
        try:
            if(parent == 0):
                checkfile = Variables.playonlinux_rep+"wineprefix/"+selection+"/playonlinux.log"
                self.logfile = open(checkfile, 'r')
                self.logsize = os.path.getsize(checkfile)
                self.logname = selection
                self.initLogDisplay()
                self.logtype = 0
                self.reportProblem.Hide()

            if(parent == 1):
                checkfile = Variables.playonlinux_rep+"logs/"+selection+"/"+selection+".log"
                self.logfile = open(checkfile, 'r')
                self.logsize = os.path.getsize(checkfile)
                self.logname = selection
                self.initLogDisplay()
                self.logtype = 1
                if(os.environ["DEBIAN_PACKAGE"] == "FALSE"):
                    self.reportProblem.Show()
                    self.reportProblem.Enable(True)
                    self.reportProblem.SetLabel(_("Report a problem about {0}").format(self.logname))

        except:
            pass

    def initLogDisplay(self):
        self.throttling = False
        self.need_redisplay = False
        self.line_buffer = ""
        self.log_reader.Clear()
        if not self.log_reader.IsFrozen():
            self.log_reader.Freeze()
        if self.logsize > 10000:
            self.logfile.seek(self.logsize - 10000) # 10000 latest chars should be sufficient
        else:
            self.logfile.seek(0)


    def list_software(self):
        self.prefixes = os.listdir(Variables.playonlinux_rep+"wineprefix/")
        self.prefixes.sort()

        self.logs = os.listdir(Variables.playonlinux_rep+"logs/")
        self.logs.sort()

        try:
            self.prefixes.remove(".DS_Store")
        except:
            pass

        self.list_game.DeleteAllItems()
        self.images.RemoveAll()

        root = self.list_game.AddRoot("")
        self.scripts_entry = self.list_game.AppendItem(root, _("Install scripts"), 1)
        self.prefixes_entry = self.list_game.AppendItem(root, _("Virtual drives"), 0)

        self.file_icone = Variables.playonlinux_env+"/resources/images/icones/generic.png"
        self.bitmap = wx.Image(self.file_icone)
        self.bitmap.Rescale(16,16,wx.IMAGE_QUALITY_HIGH)
        self.bitmap = self.bitmap.ConvertToBitmap()
        self.images.Add(self.bitmap)
        self.images.Add(self.bitmap)


        self.i = 2
        for prefix in self.prefixes:
            if(os.path.isdir(Variables.playonlinux_rep+"wineprefix/"+prefix)):

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

                self.prefixes_item[prefix] = self.list_game.AppendItem(self.prefixes_entry, prefix, self.i)
                self.i += 1

        for log in self.logs:
            if(not "_" in log and os.path.isdir(Variables.playonlinux_rep+"logs/"+log)):
                self.file_icone =  Variables.playonlinux_env+"/resources/images/menu/manual.png"

                try:
                    self.bitmap = wx.Image(self.file_icone)
                    self.bitmap.Rescale(16,16,wx.IMAGE_QUALITY_HIGH)
                    self.bitmap = self.bitmap.ConvertToBitmap()
                    self.images.Add(self.bitmap)
                except:
                    pass

                self.logs_item[log] = self.list_game.AppendItem(self.scripts_entry, log, self.i)
                self.i += 1

        self.list_game.Collapse(self.scripts_entry)
        self.list_game.Collapse(self.prefixes_entry)
        self.list_game.ExpandAll()

    def app_Close(self, event):
        self.Destroy()

    def apply_settings(self, event):
        self.Destroy()

    def Destroy(self):
        self.timer.Stop()
        return super().Destroy()
