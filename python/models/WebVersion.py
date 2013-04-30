#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python

from lib.Environement import Environement
from lib.Downloader import Downloader
from lib.PlayOnLinux import PlayOnLinux
from lib.Version import Version
from lib.File import File

class ErrWebsiteUnavailable(Exception):
   def __str__(self):
      return repr(_("PlayOnLinux website is not available"))
    
class WebVersion(Version):
    def __init__(self):
        self.context = PlayOnLinux()
        self.version = self.getWebVersion()
        
    def getWebVersion(self):
        if(self.context.getOS() == "Mac"):
            fichier_online="version_mac"
        else:
            fichier_online="version2"
        
        url = Environement().getSetting("SITE")+"/"+fichier_online+".php?v="+self.context.getAppVersion().getStringVersion()
        
        latestVersionDownload = Downloader(url, File.generateTmpFile().getPath())
        latestVersionDownload.start()
        latestVersionDownload.waitEnd()
        
        if(latestVersionDownload.hasFailed()):
            raise ErrWebsiteUnavailable
            
        return latestVersionDownload.getContent()