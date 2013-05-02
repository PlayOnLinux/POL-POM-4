#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

# python imports
import os, string, shutil

# playonlinux imports
from services.ConfigFile import ConfigFile


class Prefix():
   def __init__(self, prefixName):
       self.env = Environment()
       self.selectedPrefix = prefixName
       
   def getName(self):
       return self.selectedPrefix
       
   def getConfigFilePath(self):
       return self.getPath()+"/playonlinux.cfg"

   def getConfigFile(self):
       # Return the config file object corresponding to the config file in the prefix
       return getConfigFile(self.getConfigFilePath())
       
   def getPath(self):
       return self.context.getUserRoot()+"/wineprefix/"+self.selectedPrefix
             
   def exists(self):
       # Return true if the prefix exists
       return os.path.exists(self.getPath())
       
   def created(self):
       return os.path.exists(self.getPath()+"/drive_c")
          
   def getWineVersionString(self):
       return self.getConfigFile().getSetting("WINEVERSION")

   def getArch(self):
       arch = self.getConfigFile().getSetting("ARCH")
       if(arch == ""):
           return "x86"
       else:
           return arch
   
   def getWineVersion():
       return WineVersion(self.context, self.getWineVersion(), self.getArch())
       
   def getShortcutList(self):
       existing_shortcuts = Shortcut.getList()
       suitableShortcuts = []
       for shortcut in existing.shortcuts:
           if(shortcut.getPrefix().getName() == self.getName()):
               suitableShortcuts.append(shortcut)
       return suitableShortcuts
            
   def delete(self):
       if(self.getName() == "default"):
           return 1
       else:
           for shortcut in self.getShortcutList():
               shortcut.delete()
           
           shutil.rmtree(self.getPath())   
       
       return 0
           
   def openFolder(self):
      AppDir = self.getPath()
      if AppDir != "":
        if(os.environ["POL_OS"] == "Mac"):
            os.system("open "+AppDir)
        else:
            os.system("xdg-open "+AppDir)
        
   def createPath(self):
       os.makedirs(self.getPath())
       
   def createLog(self):
       open(self.getPath()+"/playonlinux.log","a").write("")
       
   def LoadRegValues(values):
       cfile = self.getPath()+"/user.reg"
       result = {}


       for element in values:
           result[element] = "default"

       try:
           fichier = open(cfile,"r").readlines()
       except:
           return result

       for line in fichier:
           line = line.replace("\n","")
           found = False
           for element in values:
               if(element in line):
                   line = line.replace("\"","")
                   line = string.split(line, "=")
                   line = line[1]
                   result[element] = line
                   found = True
                   break

       return(result)
       
   def wine(self, exePath, exeArgs = [], errors = True):
       # Fixme : Add FORCE_OSX_DOCK support?
       
       self.createPath()
       self.createLog()
       
       globalConfigFile = GlobalConfigFile()
       
       if(globalConfigFile.getSetting("NO_FSCHECK") != "TRUE"):
           FIXME("FILE SYSTEM CHECK HERE")
         
       """
       POL_Wine ()
       {
       	if [ "$POL_OS" = "Mac" -a "$FORCE_OSX_DOCK" ]; then
       		POL_Wine_Dock "$@"
       		return "$?"
       	fi
       	# Run the good wineversion and store the result to a logfile
       	# Same usage than "wine"
       	mkdir -p "$WINEPREFIX"
       	touch "$WINEPREFIX/playonlinux.log"
       	local NoErrors
       	if [ "$1" = "--ignore-errors" ]; then
       		NoErrors="True"
       		shift
       	fi
	
       	if [ ! "$(POL_Config_Read NO_FSCHECK)" = "TRUE" ]; then
       		if [ "$1" = "start" ]; then
       			if [ "$2" = "/unix" ]; then
       				POL_System_CheckFS "$3"
       			else
       				POL_System_CheckFS "$2"
       			fi
       		else
       			POL_System_CheckFS "$1"
       		fi
       	else
       		POL_Debug_Message "** Filesystem checks disabled **"
       	fi

       	POL_Wine_AutoSetVersionEnv
       	POL_Debug_Message "Running wine-$POL_WINEVERSION "$@" (Working directory : $PWD)"
       	POL_Debug_LogToPrefix "Running wine-$POL_WINEVERSION "$@" (Working directory : $PWD)"
       	if [ ! "$WINEMENUBUILDER_ALERT" ]; then
       		POL_Debug_Message "Notice: PlayOnLinux deliberately disables winemenubuilder. See http://www.playonlinux.com/fr/page-26-Winemenubuilder.html"
       		WINEMENUBUILDER_ALERT="Done"
       	fi
       	if [ "$1" = "regedit" -a ! "$2" = "" ]; then
       		if [ -e "$2" ]; then
       			POL_Debug_LogToPrefix "Content of $2"
       			(echo '-----------'
       			 cat "$2"
       			 echo '-----------') >> "$WINEPREFIX/playonlinux.log"
       		else
       			POL_Debug_LogToPrefix "regedit parameter '$2' is not a file, not dumped to log"
       		fi
       	elif [ "$1" = "regedit" ]; then
       		POL_Debug_LogToPrefix "User modified something in the registry manually"
       	fi


       	if [ "$LOGFILE" = "/dev/null" ]; then
       		$BEFORE_WINE $(POL_Config_Read BEFORE_WINE) wine "$@"  2> >(grep -v menubuilder --line-buffered | tee -a "$WINEPREFIX/playonlinux.log" >&2) > >(tee -a "$WINEPREFIX/playonlinux.log")
       		errors=$?
       	else
       		$BEFORE_WINE $(POL_Config_Read BEFORE_WINE) wine "$@" 2> >(grep -v menubuilder --line-buffered | tee -a "$LOGFILE" "$WINEPREFIX/playonlinux.log" >&2) > >(tee -a "$LOGFILE" "$WINEPREFIX/playonlinux.log")
       		errors=$?
       	fi

       	if [ "$errors" != 0 -a "$NoErrors" != "True" -a "$POL_IgnoreWineErrors" != "True" ]; then
       		POL_Debug_Error "$(eval_gettext 'Wine seems to have crashed\n\nIf your program is running, just ignore this message')"
       	fi
       	POL_Debug_Message "Wine return: $errors"
       	return $errors
       }
       """
          
   @staticmethod
   def getList(context):
       prefixList = os.listdir(context.getUserRoot())
       prefixList.sort()
       
       # Get a list of object instead of a list of strings
       for ndx, member in enumerate(prefixList):
           prefixList[ndx] = Prefix(prefixList[ndx])
           
       return prefixList
   
             
