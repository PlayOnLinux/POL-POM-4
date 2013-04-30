#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, wx

# playonlinux imports
from lib.PlayOnLinux import PlayOnLinux

class UIHelper(object):
   
   def getFontTitle(self):
       if(PlayOnLinux().getOS() == "Mac"):
           textSize = 14;
       else:
           textSize = 10;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
       
   def getFontText(self):
       if(PlayOnLinux().getOS() == "Mac"):
           textSize = 12;
       else:
           textSize = 8;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)

   def addMacOffset(self, size):
       if(PlayOnLinux().getOS() == "Mac"):
           return size;
       else:
           return 0;
           
   def addWindowMacOffset(self):
       return self.addMacOffset(20)
       
       
   def widgetBorders(self):
       if(PlayOnLinux().getOS() == "Mac"):
           return wx.SIMPLE_BORDER
       else:
           return wx.RAISED_BORDER
   
   def updateJaugeMarginTop(self):
       if(PlayOnLinux().getOS() == "Mac"):
           return 2
       else:
           return 6      