#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python

from lib.ConfigFile import FiletypeConfigFile
from Script import PrivateScript
from lib.Tools import uniqid
from lib.Context import Context

import wx

class File(object):
   def __init__(self, path):
       self.path = path
       self.context = Context()
 
   def getPath(self):
       return self.path
       
   def getFileType(self): 
       file_extension = string.split(self.path,".")
       file_extension = file_extension[len(file_extension) - 1]
       return file_extension.lower()
       
   def openCleverWay(self):
       extension = self.getFileType()
       if(extension == "exe"):
           PrivateScript(self.context, "run_exe", [filename]).runPoll()
           
       elif(extension == "pol" or file_extension == "POL"):
           if(wx.YES == wx.MessageBox(_('Are you sure you want to install {0} package?').format(filename).decode("utf-8","replace"), self.context.getAppName(),style=wx.YES_NO | wx.ICON_QUESTION)):
               PrivateScript(self.context, "playonlinux-pkg", ["-i", filename]).runPoll()
       else:
           self.openWithPOL()
           
   def openWithPOL(self):
       extensionList = FiletypeConfigFile()
       
       shortcutName = extensionList.getSettings(self.getFileType)
       if(shortcutName == ""):
           wx.MessageBox(_("There is nothing installed to run .{0} files.").format(ext),os.environ["APPLICATION_TITLE"], wx.OK)
       else:
           shortcut = Shortcut(self.context, shortcutName)
           windowsPath = shortcut.windowPath(self.path)
           
           shortcut.setArgs(shortcut.windowPath(path))
           shortcut.runPoll()
           

   @staticmethod
   def generateTmpFile():
       polTmpDirectory = Context().getUserRoot()+"/tmp/"
       filePath = polTmpDirectory+uniqid()+".tmp"
       return File(filePath)
       
    