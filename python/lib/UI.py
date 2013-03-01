#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string

# playonlinux imports
import Variables, wx

class UI():
   def __init__(self, context):
       self.context = context;

   def getFontTitle(self):
       if(self.context.getOS() == "Mac"):
           textSize = 14;
       else:
           textSize = 10;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
       
   def getFontText(self):
       if(self.context.getOS() == "Mac"):
           textSize = 12;
       else:
           textSize = 8;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)

   def AddMacOffset(self, size):
       if(self.context.getOS == "Mac"):
           return size;
       else:
           return 0;