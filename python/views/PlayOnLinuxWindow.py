#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

import wx

from views.UIHelper import UIHelper

class PlayOnLinuxWindow(wx.Frame):
    
    def __init__(self, controller):
        self.controller = controller
        self.uiHelper = UIHelper(controller) 