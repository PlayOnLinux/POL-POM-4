#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import string

# playonlinux imports
import Variables, ConfigFile

SHORTCUTS_PATH = Variables.pol_user_root+"/shortcuts/"

class Shortcut(Script):
   def __init__(self, shortcutName):
      self.selectedShortcut = shortcutName;
      self.path = SHORTCUTS_PATH+self.selectedShortcut
      self.needSignature = False
   # Get the shortcut script path
   def getPath(self):
       return self.path;
   
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

       if(Variables.pol_os == "Mac"):
          dirStoreName="PlayOnMac"
       else:
          dirStoreName=".PlayOnLinux"
          
       prefix = Prefix(prefix[prefix.index(dirStoreName) + 2])
       

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
     

         
   @staticmethod
   def getList():
       shortcutList = os.listdir(SHORTCUTS_PATH)
       shortcutList.sort()
       
       # Get a list of object instead of a list of strings
       for ndx, member in enumerate(shortcutList):
           shortcutList[ndx] = Shortcut(shortcutList[ndx])
           
       return shortcutList