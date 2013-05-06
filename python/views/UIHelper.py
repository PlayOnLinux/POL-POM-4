#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports

from services.Environment import Environment

import wx, os

class UIHelper(object):
   def __init__(self):
       self.env = Environment()
       
   def getFontTitle(self):
       if(self.env.getOS() == "Mac"):
           textSize = 14;
       else:
           textSize = 10;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
       
   def getFontText(self):
       if(self.env.getOS() == "Mac"):
           textSize = 12;
       else:
           textSize = 8;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)

   def addMacOffset(self, size):
       if(self.env.getOS() == "Mac"):
           return size;
       else:
           return 0;
           
   def addWindowMacOffset(self):
       return self.addMacOffset(20)
       
       
   def widgetBorders(self):
       if(self.env.getOS() == "Mac"):
           return wx.SIMPLE_BORDER
       else:
           return wx.RAISED_BORDER
   
   def updateJaugeMarginTop(self):
       if(self.env.getOS() == "Mac"):
           return 2
       else:
           return 6      

   def getBitmap(self, name, size = None):
       os.chdir(self.env.getAppPath()+"/resources/images/")
       if(size == None):
           return wx.Bitmap(name)
       else:
           bitmap = wx.Image(name)
           bitmap.Rescale(size, size, wx.IMAGE_QUALITY_HIGH)
           bitmap = bitmap.ConvertToBitmap()
           return bitmap
           
   def getIcon(self, icone):
       return wx.Icon(self.env.getAppPath()+"/resources/icons/"+icone, wx.BITMAP_TYPE_ANY)