#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os, time
from lib.Context import Context

from lib.ConfigFile import GlobalConfigFile 
from lib.ConfigFile import CustomConfigFile
from lib.ConfigFile import UserConfigFile

from lib.Environement import Environement


class Executable(object):
   def __init__(self, path, args):
       
      self.path = path[:]
      self.args = args[:]  
      self.execEnv = Environement()
      self.setEnv()
      
   def getProgramArray(self):
       args = self.args[:]
       args.insert(0,self.path)
       return args

   # Set environement vars from context and from config file
   def setPath(self):
       execEnv = self.execEnv
       execEnv.setEnv("WINEDLLOVERRIDES","winemenubuilder.exe=d")
       
       if (Context().getOS() == "Mac"):
          execEnv.setEnv("PATH" , execEnv.getAppPath()+"/../unix/wine/bin:" + execEnv.getAppPath()+"/../unix/image_magick/bin:" + execEnv.getAppPath()+"/../unix/tools/bin/:" + execEnv.getEnv("PATH") )
          execEnv.setEnv("LD_LIBRARY_PATH" , execEnv.getAppPath()+"/../unix/wine/lib/:"  + execEnv.getAppPath()+"/../unix/image_magick/lib:"+ execEnv.getAppPath()+"/../unix/tools/lib/ld:/usr/X11/lib/:" + execEnv.getEnv("LD_LIBRARY_PATH") )
          execEnv.setEnv("DYLD_LIBRARY_PATH" ,  execEnv.getAppPath()+"/../unix/tools/lib/dyld:" + execEnv.getAppPath()+"/../unix/image_magick/lib:"+ execEnv.getEnv("DYLD_LIBRARY_PATH") )
       
       
       if(os.path.exists("/usr/lib/wine/wineserver")): 
           execEnv.setEnv("PATH" , execEnv.getEnv("PATH")+":/usr/lib/wine/")
       elif(os.path.exists("/usr/lib32/wine/wineserver")):
           execEnv.setEnv("PATH" , execEnv.getEnv("PATH")+":/usr/lib32/wine/")
       elif(os.path.exists("/usr/lib/wine-unstable/wineserver")):
           execEnv.setEnv("PATH" , execEnv.getEnv("PATH")+":/usr/lib/wine-unstable/")
       elif(os.path.exists("/usr/lib32/wine-unstable/wineserver")):
           execEnv.setEnv("PATH" , execEnv.getEnv("PATH")+":/usr/lib32/wine-unstable/")
       elif(os.path.exists("/usr/lib/i386-linux-gnu/wine-unstable/wineserver")):
           execEnv.setEnv("PATH" , execEnv.getEnv("PATH")+":/usr/lib/i386-linux-gnu/wine-unstable/")
       elif(os.path.exists("/usr/lib/i386-linux-gnu/wine-stable/wineserver")):
           execEnv.setEnv("PATH" , execEnv.getEnv("PATH")+":/usr/lib/i386-linux-gnu/wine-stable/")
           
   # Some environement vars need to be set before running bash inside POL
   def setEnv(self):     
       execEnv = self.execEnv
       
       # Depend on the context
       execEnv.setEnv("PLAYONLINUX", Context().getAppPath())
       
       # Should not be needed anymore, but some scripts still checks PLAYONMAC existence
       if(Context().getOS() == "Mac"):
           execEnv.setEnv("PLAYONMAC", Context().getAppPath())
           
       # POL_USER_ROOT
       execEnv.setEnv("REPERTOIRE", Context().getUserRoot()) # ( Backward compatibility )
       execEnv.setEnv("POL_USER_ROOT", Context().getUserRoot())
       
       # WGET
       execEnv.setEnv("WGETRC", Context().getUserRoot()+"/configurations/wgetrc")
       if(os.path.exists("/proc/net/if_inet6") or Context().getOS == "Mac"):
           execEnv.setEnv("POL_WGET","wget --prefer-family=IPv4 -q")
       else:
           execEnv.setEnv("POL_WGET","wget -q")
       
       # Proxy
 
       if(execEnv.getSetting("PROXY_ENABLED") == "1"):
          if(execEnv.getSetting("PROXY_URL") != ""):
               if(execEnv.getSetting("PROXY_LOGIN") == ""):
                   http_proxy = "http://"+execEnv.getSetting("PROXY_URL")+":"+execEnv.getSetting("PROXY_PORT")
               else:
                   http_proxy = "http://"+execEnv.getSetting("PROXY_LOGIN")+":"+execEnv.getSetting("PROXY_PASSWORD")+"@"+execEnv.getSetting("PROXY_URL")+":"+execEnv.getSetting("PROXY_PORT")
               execEnv.setEnv("http_proxy", http_proxy)
               
       # Image Magick on OSX     
       if(Context().getOS() == "Mac"):
          execEnv.setEnv("MAGICK_HOME",Context().getAppPath()+"/../unix/image_magick/")
           
       # Reading from config files
       
       # Config files
       for key in ["SITE", "VERSION", "WINE_SITE", "GECKO_SITE", "DEBIAN_PACKAGE", "APPLICATION_TITLE", "DNS"]:
           execEnv.setEnv(key, execEnv.getSetting(key))
       
       
       self.setPath()

       
   def callPopen(self):
       myProcess = subprocess.Popen(self.getProgramArray(), stdout = subprocess.PIPE, preexec_fn = lambda: os.setpgid(os.getpid(), os.getpid()), env = self.execEnv.get())
       return myProcess
    
   def runSilently(self):
      devnull = open('/dev/null', 'wb')
      myProcess = subprocess.Popen(self.getProgramArray(), stdout = devnull, env = self.execEnv.get())
      return myProcess.wait()
      
   def run(self):
      myProcess = subprocess.Popen(self.getProgramArray(), env = self.execEnv.get())
      return myProcess.wait()

   def runPoll(self):
      myProcess = self.callPopen()
      return myProcess

   def runBackground(self):
       subprocess.Popen(self.getProgramArray(), env = self.execEnv.get())
       