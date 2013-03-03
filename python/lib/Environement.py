#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

from lib.Context import Context
import os, string, wx, gettext

class Environement(object):
   instance = None    
   def __new__(myClass):
        if(myClass.instance is None):
            myClass.instance = object.__new__(myClass)
        return myClass.instance
        
   def __init__(self):
      try: 
          self.alreadyInit
      except AttributeError:
          self.alreadyInit = True
          self.initEnvironement()
     
   def initEnvironement(self):     
      self.pol_os = self.getEnv("POL_OS")
      if(self.pol_os == ""):
          print "ERROR ! Please define POL_OS environment var first."
          os._exit(1)
      else:
          Context().setOS(self.pol_os)
     
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
          
      #self.setEnv("AMD64_COMPATIBLE",str(self.is64bit()).upper())
      self.setEnv("POL_USER_ROOT",self.getEnv("REPERTOIRE"))
      self.setEnv("WGETRC", self.getUserRoot()+"/configurations/wgetrc")
      self.initWineEnvironement()
      
   def initPOLself(self):
      
      self.setEnv("REPERTOIRE",self.getEnv("HOME")+"/.PlayOnLinux/")
      self.setEnv("APPLICATION_TITLE","PlayOnLinux")
      self.setEnv("POL_DNS","playonlinux.com")
      
      if not os.path.exists("/proc/net/if_inet6"):
          self.setEnv("POL_WGET","wget -q")
      else:
          self.setEnv("POL_WGET","wget --prefer-family=IPv4 -q")
          
      #Context().getUI().windows_add_size = 0;
      #windows_add_playonmac = 0;
      #widget_borders = wx.RAISED_BORDER
      Context().setAppName("PlayOnLinux")
          
   def initPOMEnvironement(self):
      self.setEnv("PLAYONMAC",self.getEnv("PLAYONLINUX"))
      self.setEnv("REPERTOIRE",self.getEnv("HOME")+"/Library/PlayOnMac/")
      self.setEnv("APPLICATION_TITLE","PlayOnMac")
      self.setEnv("POL_DNS","playonmac.com")
      self.setEnv("POL_WGET","wget --prefer-family=IPv4 -q")
      
      #windows_add_size = 20;
      #windows_add_playonmac = 1;
      #widget_borders = wx.SIMPLE_BORDER

      # Image Magick on OSX
      self.setEnv("MAGICK_HOME",self.getAppPath()+"/../unix/image_magick/")
      Context().setAppName("PlayOnMac")
      
   def initWineEnvironement(self):
      self.setEnv("WINEDLLOVERRIDES","winemenubuilder.exe=d")

      self.fixWineOnDebian()
      if (Context().getOS() == "Mac"):
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
         
   def getAppPath(self):
          return os.path.realpath(os.path.realpath(__file__)+"/../../../") 
   
   def setEnv(self, var, content):
        os.environ[var] = content
               
   def getEnv(self, var):
      try :
         return os.environ[var]
      except KeyError:
         return ""
      
      
   def getArch(self):
       archi = string.split(self.getEnv("MACHTYPE"),"-")
       return archi[0]
       
 
   
   def getUserRoot(self):
       return self.getEnv("POL_USER_ROOT") 
          
       
   def createContext(self):
       Context().setAppPath(self.getAppPath()) 
       Context().setUserRoot(self.getUserRoot()) 
       
       if(self.getArch() == "x86_64" and self.pol_os == "Linux"):
           Context().set64bit(True)
       else:
           Context().set64bit(False)
           
       Context().setDebianPackage((os.environ["DEBIAN_PACKAGE"] == "TRUE"))
       
              