#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

import wx

from controllers.Controller import *

class Modal():
   def __init__(self, content):
      self.configService = ConfigService()
      self.title = self.configService.getAppName() 
      self.content = content
      self.show()
      
   def show(self):
       content = self.content.replace("[APP]",self.configService.getAppName())
       wx.MessageBox(content, self.title)