#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from views.Modal import Modal
from controllers.Controller import *


import wx

class Question(Modal):
   def __init__(self, content): 
      self.title = Context().getAppName()
      
      self.answer = False
      self.content = content
      self.show()
       
   def show(self):
       content = self.content.replace("[APP]",Controller().getAppName())
       self.answer = (wx.YES == wx.MessageBox(content, self.title, style=wx.YES_NO | wx.ICON_QUESTION))
   
   def getAnswer(self):
       return self.answer