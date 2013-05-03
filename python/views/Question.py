#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from services.ConfigService import ConfigService
from views.Modal import Modal

import wx

class Question(Modal):
   def __init__(self, content): 
      self.configService = ConfigService()
      self.title = self.configService.getAppName()
      
      self.answer = False
      self.content = content
      self.show()
       
   def show(self):
       content = self.content.replace("[APP]",self.title)
       self.answer = (wx.YES == wx.MessageBox(content, self.title, style=wx.YES_NO | wx.ICON_QUESTION))
   
   def getAnswer(self):
       return self.answer