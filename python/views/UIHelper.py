#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, wx


class ErrNoController(Exception):
    def __str__(self):
       return repr(_("Controller is not set"))
       
class UIHelper(object):
   def __init__(self, controller = None):
       self.controller = controller
       
   def getFontTitle(self):
       if(self.controller == None):
          raise ErrNoController
       if(self.controller.getOS() == "Mac"):
           textSize = 14;
       else:
           textSize = 10;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
       
   def getFontText(self):
       if(self.controller == None):
          raise ErrNoController
       if(self.controller.getOS() == "Mac"):
           textSize = 12;
       else:
           textSize = 8;
           
       return wx.Font(textSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)

   def addMacOffset(self, size):
       if(self.controller == None):
          raise ErrNoController
       if(self.controller.getOS() == "Mac"):
           return size;
       else:
           return 0;
           
   def addWindowMacOffset(self):
       return self.addMacOffset(20)
       
       
   def widgetBorders(self):
       if(self.controller.getOS() == "Mac"):
           return wx.SIMPLE_BORDER
       else:
           return wx.RAISED_BORDER
   
   def updateJaugeMarginTop(self):
       if(self.controller.getOS() == "Mac"):
           return 2
       else:
           return 6      

   def getImage(self, name):
       return None
     
   def getIcon(self, icone):
       if(self.controller == None):
          raise ErrNoController
       return wx.Icon(self.controller.getAppPath()+"/icons/"+icone, wx.BITMAP_TYPE_ANY)