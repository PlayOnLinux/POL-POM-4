#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python

from lib.ConfigFile import FiletypeConfigFile
from lib.PlayOnLinux import PlayOnLinux
import wx, os

class WineVersion(object):
    def __init__(self, version, arch):
        self.context = PlayOnLinux()
        self.version = version
        self.arch = arch
        
    def getPath(self):
        if(version == ""):
            return ""
        else:
            return self.context.getUserRoot()+"/wine/"+self.context.getOSCodeName()+"-"+arch+"/"+version+"/"
         
    def exists(self):
        if(version == ""):
            return True
        else:
            return os.path.exists(self.getPath())  
            
    def getWineBinary(self):
        if(version = ""):
            return "wine"
        else:
            return getPath+"/usr/bin/wine"
        
       