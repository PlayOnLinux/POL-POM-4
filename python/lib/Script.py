#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os
from lib.Context import Context

from lib.ConfigFile import GlobalConfigFile 
from lib.ConfigFile import CustomConfigFile
from lib.ConfigFile import UserConfigFile

from lib.Environement import Environement

class ErrBadSignature(Exception):
   def __str__(self):
      return repr(_("The signature of the script is wrong"))

class Script(object):
   def __init__(self, path, args):
      self.path = path
      self.args = args
      self.needSignature = True
      
      return True
      
   # Fixme
   def checkSignature(self): 
                
       # Fixme
       return True
       
   def getProgramArray(self, args = []):
       args.insert(0,self.path)
       args.insert(0,"bash")
       return args
        
   # Set environement vars from context and from config file
   def setPath(self):
       Environement().setEnv("WINEDLLOVERRIDES","winemenubuilder.exe=d")
       
       if (Context().getOS() == "Mac"):
          Environement().setEnv("PATH" , Environement().getAppPath()+"/../unix/wine/bin:" + Environement().getAppPath()+"/../unix/image_magick/bin:" + Environement().getAppPath()+"/../unix/tools/bin/:" + Environement().getEnv("PATH") )
          Environement().setEnv("LD_LIBRARY_PATH" , Environement().getAppPath()+"/../unix/wine/lib/:"  + Environement().getAppPath()+"/../unix/image_magick/lib:"+ Environement().getAppPath()+"/../unix/tools/lib/ld:/usr/X11/lib/:" + Environement().getEnv("LD_LIBRARY_PATH") )
          Environement().setEnv("DYLD_LIBRARY_PATH" ,  Environement().getAppPath()+"/../unix/tools/lib/dyld:" + Environement().getAppPath()+"/../unix/image_magick/lib:"+ Environement().getEnv("DYLD_LIBRARY_PATH") )
       
       
       if(os.path.exists("/usr/lib/wine/wineserver")): 
           Environement().setEnv("PATH" , Environement().getEnv("PATH")+":/usr/lib/wine/")
       elif(os.path.exists("/usr/lib32/wine/wineserver")):
           Environement().setEnv("PATH" , Environement().getEnv("PATH")+":/usr/lib32/wine/")
       elif(os.path.exists("/usr/lib/wine-unstable/wineserver")):
           Environement().setEnv("PATH" , Environement().getEnv("PATH")+":/usr/lib/wine-unstable/")
       elif(os.path.exists("/usr/lib32/wine-unstable/wineserver")):
           Environement().setEnv("PATH" , Environement().getEnv("PATH")+":/usr/lib32/wine-unstable/")
       elif(os.path.exists("/usr/lib/i386-linux-gnu/wine-unstable/wineserver")):
           Environement().setEnv("PATH" , Environement().getEnv("PATH")+":/usr/lib/i386-linux-gnu/wine-unstable/")
       elif(os.path.exists("/usr/lib/i386-linux-gnu/wine-stable/wineserver")):
           Environement().setEnv("PATH" , Environement().getEnv("PATH")+":/usr/lib/i386-linux-gnu/wine-stable/")
           
   # Some environement vars need to be set before running bash inside POL
   def setEnv(self):     
      
       
       # Depend on the context
       Environement().setEnv("PLAYONLINUX", Context().getAppPath())
       
       # Should not be needed anymore, but some scripts still checks PLAYONMAC existence
       if(Context().getOS() == "Mac"):
           Environement().setEnv("PLAYONMAC", Context().getAppPath())
           
       # POL_USER_ROOT
       Environement().setEnv("REPERTOIRE", Context().getUserRoot()) # ( Backward compatibility )
       Environement().setEnv("POL_USER_ROOT", Context().getUserRoot())
       
       # WGET
       Environement().setEnv("WGETRC", Context().getUserRoot()+"/configurations/wgetrc")
       if(os.path.exists("/proc/net/if_inet6") or Context().getOS == "Mac"):
           Environement().setEnv("POL_WGET","wget --prefer-family=IPv4 -q")
       else:
           Environement().setEnv("POL_WGET","wget -q")
       
       # Proxy
       self.uConfig = UserConfigFile()
       if(self.uConfig.getSetting("PROXY_ENABLED") == "1"):
          if(self.uConfig.getSettings("PROXY_URL") != ""):
               if(playonlinux.getSetting("PROXY_LOGIN") == ""):
                   http_proxy = "http://"+self.uConfig.getSetting("PROXY_URL")+":"+self.uConfig.getSetting("PROXY_PORT")
               else:
                   http_proxy = "http://"+self.uConfig.getSetting("PROXY_LOGIN")+":"+self.uConfig.getSetting("PROXY_PASSWORD")+"@"+self.uConfig.getSetting("PROXY_URL")+":"+self.uConfig.getSetting("PROXY_PORT")
               Environement().setEnv("http_proxy", http_proxy)
               
       # Image Magick on OSX     
       if(Context().getOS() == "Mac"):
          Environement().setEnv("MAGICK_HOME",Context().getAppPath()+"/../unix/image_magick/")
           
       # Reading from config files
       
       # Global config file
       self.gConfig = GlobalConfigFile()
       for key in ["SITE", "VERSION", "WINE_SITE", "GECKO_SITE", "DEBIAN_PACKAGE"]:
           Environement().setEnv(key,self.gConfig.getSetting(key))
       
       # Specific config file
       self.cConfig = CustomConfigFile()
       for key in ["APPLICATION_TITLE", "POL_DNS"]:
           Environement().setEnv(key,self.cConfig.getSetting(key))
       
       
       
       self.setPath()
       
   def run(self):
       self.setEnv()
       if(self.checkSignature() or not self.needSignature):
          try:
               returncode = subprocess.call(self.getProgramArray(self.args))
               return returnCode
          except:
              return 255
       else:
          raise ErrBadSignature

   def runPoll(self):
       self.setEnv()
       if(self.checkSignature() or not self.needSignature):
           return subprocess.Popen(self.getProgramArray(self.args), stdout = subprocess.PIPE, preexec_fn = lambda: os.setpgid(os.getpid(), os.getpid()))

class PrivateScript(Script):
   def __init__(self, path, args = []):
      self.context = Context()
      
      self.path = self.context.getAppPath()+"/bash/"+path
      self.args = args
      self.needSignature = False
      
class GUIScript(Script):
    def setEnv():
        # Set by the GUI server
        Environement().setEnv("POL_PORT", Context().getPOLServer().getRunningPort())
        Environement().setEnv("POL_COOKIE", Context().getPOLServer().getCookie())
  
        Script.setEnv(self)