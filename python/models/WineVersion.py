#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python

from services.Environment import Environment


from lib.ConfigFile import FiletypeConfigFile
from lib.PlayOnLinux import PlayOnLinux


class WineVersion(object):
    def __init__(self, version, arch):
        self.env = Environment()
        self.version = version
        self.arch = arch
        
    def getPath(self):
        if(version == ""):
            return ""
        else:
            return self.env.getUserRoot()+"/wine/"+self.env.getOSCodeName()+"-"+arch+"/"+version+"/"
         
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
        
       