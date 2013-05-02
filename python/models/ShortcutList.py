#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, os, wx

from models.Observable import Observable
from models.Timer import Timer
from models.Shortcut import Shortcut

class ShortcutList(Observable):
   def __init__(self, shortcutList = []):
       self.shortcutList = shortcutList[:]
       
   def get(self):
       return self.shortcutList
       
class ShortcutListFromFolder(ShortcutList):
   def __init__(self, folder):
       Observable.__init__(self)
       self.folder = folder

       shortcutList = self.getShortcutsFromFolder()
       ShortcutList.__init__(self, shortcutList)
       self.folderTime = None
        
   def getShortcutsFolderTime(self):
       return os.path.getmtime(self.folder)
       
   def getShortcutsFromFolder(self):
       shortcutList = os.listdir(self.folder)
       shortcutList.sort()
       
       # FIXME
       try :
           shortcutList.remove(".DS_Store")
       except ValueError:
           pass
           
       # Get a list of object instead of a list of strings
       for ndx, member in enumerate(shortcutList):
           shortcutList[ndx] = Shortcut(member)
       return shortcutList
      
   # Timer
   def checkFromChange(self, tempo = 1.0):
       timer = Timer(1.0, self.updateShortcutsFromFolder)
       timer.start()
      
   
   # Update shortcuts from folder, return True if changes have been made
   def updateShortcutsFromFolder(self):
        folderTime = self.getShortcutsFolderTime()
        if(folderTime != self.folderTime):
            shortcutList = self.getShortcutsFromFolder()
            self.shortcutList = shortcutList
            self.folderTime = folderTime
            changed = True
            self.update()
            
        else:
            changed = False
        
        return changed