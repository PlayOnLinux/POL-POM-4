#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, os, wx

from models.Observable import *
from models.Observer import *

from models.Shortcut import Shortcut

class ShortcutList(Observer, Observable):
   def __init__(self, shortcutList = []):
       Observable.__init__(self)
       self.shortcutList = shortcutList[:]
       
   def getList(self):
       return self.shortcutList
       
class ShortcutListFromFolder(ShortcutList):      
   def notify(self):
       shortcutList = []   
       for ndx, member in enumerate(self.subject):
           shortcutList.append(Shortcut(member))
       self.shortcutList = shortcutList
       self.update()