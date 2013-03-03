#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

import wx

from lib.Context import Context

class Modal():
   def __init__(self, title, content): 
      self.title = title
      self.content = content
      self.show()
      
   def show(self):
       content = self.content.replace("{APP}",Context().getAppName())
       wx.MessageBox(content, self.title)