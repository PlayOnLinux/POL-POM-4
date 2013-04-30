#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string, os, wx

# playonlinux imports
import ConfigFile

from lib.PlayOnLinux import PlayOnLinux
from lib.Script import PrivateGUIScript
from lib.Prefix import Prefix
from lib.Environement import Environement

class ShortcutList(object):
   def __init__(self, shortcutList = []):
       self.shortcutList = shortcutList[:]
       
   def get(self):
       return self.shortcutList
       
class ShortcutListFromFolder(ShortcutList):
   def __init__(self, folder):
       self.folder = folder

       shortcutList = self.getShortcutsFromFolder()
       ShortcutList.__init__(self, shortcutList)
       self.folderTime = self.getShortcutsFolderTime()
        
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
        
   # Update shortcuts from folder, return True if changes have been made
   def updateShortcutsFromFolder(self):
        folderTime = self.getShortcutsFolderTime()
        if(folderTime != self.folderTime):
            shortcutList = self.getShortcutsFromFolder()
            self.shortcutList = shortcutList
            changed = True
        else:
            changed = False
        
        return changed
        
class Shortcut(object):
   def __init__(self, shortcutName, args = []):
      self.args = args[:]
      self.shortcutName = shortcutName
      self.context = PlayOnLinux()
      self.shortcutPath = self.context.getUserRoot()+"/shortcuts/"+shortcutName
      
   def run(self):
       arguments = [self.shortcutName] + self.args
       self.shortcutScript = PrivateGUIScript("run_app", arguments)
       self.shortcutScript.start()
       
       
   def getName(self):
       return self.shortcutName
       
   # Get the shortcut script path
   def getPath(self):
       return self.shortcutPath;
  
   # List of script's line
   def getScriptLines(self):
       shortcutFile = open(self.getPath(),'r').read()
       shortcutFile = string.split(shortcutFile,"\n")
       return shortcutFile
       
 
   # Get the prefix object from shortcut
   def getPrefix(self): 
       shortcutFile = self.getScriptLines()
       
       i = 0
       while(i < len(shortcutFile)):
           if("export WINEPREFIX=" in shortcutFile[i]):
               break
           i += 1
           
       
       prefix = string.split(shortcutFile[i],"\"")
      
       prefix = prefix[1].replace("//","/")
       prefix = string.split(prefix,"/")

       if(self.context.getOS() == "Mac"):
          dirStoreName="PlayOnMac"
       else:
          dirStoreName=".PlayOnLinux"
          
       prefix = Prefix(self.context, prefix[prefix.index(dirStoreName) + 2])
       

       return prefix
       
   # Get shortcut args
   def getArgs(self): 
       shortcutFile = self.getScriptLines()

       i = 0
       while(i < len(shortcutFile)):
           if("POL_Wine " in shortcutFile[i]):
               break
           i += 1

       try:
           args = shlex.split(shortcutFile[i])[2:-1]
           args = " ".join([ pipes.quote(x) for x in args])
       except:
           args = ""

       return args       

   def writeArgs(game, args):
      cfile = context.getUserRoot()+"shortcuts/"+game
      fichier = open(cfile,"r").readlines()
      i = 0
      line = []

      while(i < len(fichier)):
         fichier[i] = fichier[i].replace("\n","")
         if("POL_Wine " not in fichier[i]):
            line.append(fichier[i])
         else:
            try:
               old_string = shlex.split(fichier[i])
               new_string = shlex.split(str(args))
               new_string = old_string[0:2] + new_string
               new_string = " ".join([ pipes.quote(x) for x in new_string])

               new_string = new_string+' "$@"'
               line.append(new_string)
            except:
               line.append(fichier[i])
         i += 1

      fichier_write = open(cfile,"w")
      i = 0
      while(i < len(line)): # On ecrit
         fichier_write.write(line[i]+"\n")
         i+=1


   def isDebug(self):
       try:
           shortcutFile = self.getScriptLines()
       except:
           return True

       for line in shortcutFile:
           if(line == 'export WINEDEBUG="-all"'):
               return False
           if(line == 'export WINEDEBUG=""'):
               return True
       return False

   def setDebug(self, state):
       try:
           shortcutFile = self.getScriptLines()
       except:
           return False

       lines = []
       for line in shortcutFile:
           if('export WINEDEBUG=' in line):
               if(state == True):
                   line = 'export WINEDEBUG=""'
               else:
                   line = 'export WINEDEBUG="-all"'
           lines.append(line)

       shortcutFileWrite = open(self.getPath(),"w")

       i = 0
       while(i < len(lines)): # On ecrit
           shortcutFileWrite.write(lines[i]+"\n")
           i+=1
           
   def delete(self):
       os.remove(self.getPath())
     
   def windowPath(self, unixPath):
      if(unixPath[0] != "/"):
         unixPath = os.environ["WorkingDirectory"]+"/"+unixPath
        
      path = os.path.realpath(path)
      prefix = self.getPrefix()
      
      prefixName = prefix.getName()
      
      ver = prefix.getWineVersion()
      
      if(ver.exists()):
        return(os.popen("env WINEPREFIX='"+self.prefix.getPath()+"/' '"+self.ver.getWineBinary()+"' winepath -w '"+unixPath+"'").read().replace("\n","").replace("\r",""))

   def getWxIcon(self, iconSize = 32):
       if(iconSize == 32):
           iconFolder = "32"
       else:
           iconFolder = "full_size"
           
       iconPath = PlayOnLinux().getUserRoot()+"/icones/"+iconFolder+"/"+self.getName()
       if(not os.path.exists(iconPath)):
           iconPath = PlayOnLinux().getAppPath()+"/etc/playonlinux.png"

       try:
          bitmap = wx.Image(iconPath)
          bitmap.Rescale(iconSize,iconSize,wx.IMAGE_QUALITY_HIGH)
          bitmap = bitmap.ConvertToBitmap()
          return bitmap  
          
       except wx._core.PyAssertionError: 
          iconPath = PlayOnLinux().getAppPath()+"/etc/playonlinux.png"
          bitmap = wx.Image(iconPath)
          bitmap.Rescale(iconSize,iconSize,wx.IMAGE_QUALITY_HIGH)
          bitmap = bitmap.ConvertToBitmap()
          return bitmap    
   
               
   def uninstall(self):
       print "I will uninstall "+self.getName()