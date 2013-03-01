#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2011 - Quentin PARIS

import os, random, sys, string, gettext, locale
import wx, wxversion

class Context(object):
   def __init__(self):
      self.pol_os = self.getEnv("POL_OS")
        
      self.initEnvironement()
      # Fixme. We could detect that automatically
      if(self.pol_os == "None"):
         print "ERROR ! Please define POL_OS environment var first."
         os._exit(1)
      
      
   # Bash script backward compatibility. We are going to clean that
   def initEnvironement(self):
      self.setEnv("PLAYONLINUX",self.getAppPath())
      self.setEnv("SITE","http://repository.playonlinux.com")
      self.setEnv("POL_PORT","0")
      self.setEnv("VERSION","5.0-dev")
      self.setEnv("WINE_SITE","http://www.playonlinux.com/wine/binaries")
      self.setEnv("GECKO_SITE","http://www.playonlinux.com/wine/gecko")
      self.setEnv("DEBIAN_PACKAGE", "FALSE")
      
      if(self.pol_os == "Linux"):
          self.initPOLEnvironement()

      if(self.pol_os == "Mac"):
          self.initPOMEnvironement()
          
      self.setEnv("AMD64_COMPATIBLE",str(self.is64bit()).upper())
      self.setEnv("POL_USER_ROOT",self.getEnv("REPERTOIRE"))
      self.setEnv("OS_NAME", self.os_name)
      self.setEnv("WGETRC", self.getUserRoot()+"/configurations/wgetrc")
      self.initWineEnvironement()
       
   def getAppPath(self):
       return os.path.realpath(os.path.realpath(__file__)+"/../../../")
   
   def getUserRoot(self):
       return self.getEnv("REPERTOIRE") # FIXME 
     
   def getAppName(self):
       return self.getEnv("APPLICATION_TITLE")

   def getAppVersion(self):
       return self.getEnv("VERSION")
           
   def initPOLEnvironement(self):
      self.setEnv("REPERTOIRE",self.getEnv("HOME")+"/.PlayOnLinux/")
      self.setEnv("APPLICATION_TITLE","PlayOnLinux")
      self.setEnv("POL_DNS","playonlinux.com")
      
      if not os.path.exists("/proc/net/if_inet6"):
          self.setEnv("POL_WGET","wget -q")
      else:
          self.setEnv("POL_WGET","wget --prefer-family=IPv4 -q")
          
      self.windows_add_size = 0;
      self.windows_add_playonmac = 0;
      self.widget_borders = wx.RAISED_BORDER
      self.os_name = "linux"
          
   def initPOMEnvironement(self):
      self.setEnv("PLAYONMAC",self.getEnv("PLAYONLINUX"))
      self.setEnv("REPERTOIRE",self.getEnv("HOME")+"/Library/PlayOnMac/")
      self.setEnv("APPLICATION_TITLE","PlayOnMac")
      self.setEnv("POL_DNS","playonmac.com")
      self.setEnv("POL_WGET","wget --prefer-family=IPv4 -q")
      
      self.windows_add_size = 20;
      self.windows_add_playonmac = 1;
      self.widget_borders = wx.SIMPLE_BORDER
      self.os_name = "darwin"

      # Image Magick on OSX
      self.setEnv("MAGICK_HOME",self.getAppPath()+"/../unix/image_magick/")
      
   def initWineEnvironement(self):
      self.setEnv("WINEDLLOVERRIDES","winemenubuilder.exe=d")

      self.fixWineOnDebian()
      if (os.environ["POL_OS"] == "Mac"):
         self.setEnv("PATH" , self.getAppPath()+"/../unix/wine/bin:" + self.getAppPath()+"/../unix/image_magick/bin:" + self.getAppPath()+"/../unix/tools/bin/:" + self.getEnv("PATH") )
         self.setEnv("LD_LIBRARY_PATH" , self.getAppPath()+"/../unix/wine/lib/:"  + self.getAppPath()+"/../unix/image_magick/lib:"+ self.getAppPath()+"/../unix/tools/lib/ld:/usr/X11/lib/:" + self.getEnv("LD_LIBRARY_PATH") )
         self.setEnv("DYLD_LIBRARY_PATH" ,  self.getAppPath()+"/../unix/tools/lib/dyld:" + self.getAppPath()+"/../unix/image_magick/lib:"+ self.getEnv("DYLD_LIBRARY_PATH") )
      self.savePath()
      
   def savePath(self):
       self.setEnv("PATH_ORIGIN", self.getEnv("PATH"))
       self.setEnv("LD_PATH_ORIGIN", self.getEnv("LD_LIBRARY_PATH"))
       self.setEnv("DYLDPATH_ORIGIN", self.getEnv("DYLD_LIBRARY_PATH"))

   def restorePath(self):
       self.setEnv("PATH", self.getEnv("PATH_ORIGIN"))
       self.setEnv("LD_LIBRARY_PATH", self.getEnv("LD_PATH_ORIGIN"))
       self.setEnv("DYLD_LIBRARY_PATH", self.getEnv("DYLDPATH_ORIGIN"))
       
   # Fix for a bug caused by debian's packaging
   def fixWineOnDebian(self):
       if(os.path.exists("/usr/lib/wine/wineserver")): 
           self.setEnv("PATH" , self.getEnv("PATH")+":/usr/lib/wine/")
       elif(os.path.exists("/usr/lib32/wine/wineserver")):
           self.setEnv("PATH" , self.getEnv("PATH")+":/usr/lib32/wine/")
       elif(os.path.exists("/usr/lib/wine-unstable/wineserver")):
           self.setEnv("PATH" , self.getEnv("PATH")+":/usr/lib/wine-unstable/")
       elif(os.path.exists("/usr/lib32/wine-unstable/wineserver")):
           self.setEnv("PATH" , self.getEnv("PATH")+":/usr/lib32/wine-unstable/")
       elif(os.path.exists("/usr/lib/i386-linux-gnu/wine-unstable/wineserver")):
           self.setEnv("PATH" , self.getEnv("PATH")+":/usr/lib/i386-linux-gnu/wine-unstable/")
       elif(os.path.exists("/usr/lib/i386-linux-gnu/wine-stable/wineserver")):
           self.setEnv("PATH" , self.getEnv("PATH")+":/usr/lib/i386-linux-gnu/wine-stable/")
                     
   def getArch(self):
       archi = string.split(self.getEnv("MACHTYPE"),"-")
       return archi[0]
       
   def getOS(self):
       return self.pol_os
     
   def getHomeDir(self):
       return self.getEnv("HOME")
         
   def is64bit(self):
       if(self.getArch() == "x86_64" and self.getOS() == "Linux"):
           return True
       else:
           return False
               
   def getEnv(self, var):
      try :
         return os.environ[var]
      except :
         return ""
            
   def setEnv(self, var, content):
        os.environ[var] = content

   def initLanguage(self):
       if(os.environ["DEBIAN_PACKAGE"] == "TRUE"):
           languages = os.listdir('/usr/share/locale')
       else:
           languages = os.listdir(self.getAppPath()+'/lang/locale')

       langid = wx.LANGUAGE_DEFAULT
       if(os.environ["DEBIAN_PACKAGE"] == "TRUE"):
           localedir = "/usr/share/locale"
       else:
           localedir = os.path.join(self.getAppPath(), "lang/locale")

       domain = "pol"
       mylocale = wx.Locale(langid)
       mylocale.AddCatalogLookupPathPrefix(localedir)
       mylocale.AddCatalog(domain)

       mytranslation = gettext.translation(domain, localedir, [mylocale.GetCanonicalName()], fallback = True)
       mytranslation.install()
       
"""

def proxy_initialization():
    ## Proxy settings
    if(playonlinux.GetSettings("PROXY_ENABLED") == "1"):
        if(playonlinux.GetSettings("PROXY_URL") != ""):
            if(playonlinux.GetSettings("PROXY_LOGIN") == ""):
                http_proxy = "http://"+playonlinux.GetSettings("PROXY_URL")+":"+playonlinux.GetSettings("PROXY_PORT")
            else:
                http_proxy = "http://"+playonlinux.GetSettings("PROXY_LOGIN")+":"+playonlinux.GetSettings("PROXY_PASSWORD")+"@"+playonlinux.GetSettings("PROXY_URL")+":"+playonlinux.GetSettings("PROXY_PORT")
            os.environ["http_proxy"] = http_proxy

initialization()
"""