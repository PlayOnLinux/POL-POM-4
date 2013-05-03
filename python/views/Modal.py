#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

import wx

from controllers.Controller import *

class Modal():
   def __init__(self, title, content): 
      self.title = title
      self.content = content
      self.show()
      
   def show(self):
       content = self.content.replace("[APP]",Controller().getAppName())
       wx.MessageBox(content, self.title)