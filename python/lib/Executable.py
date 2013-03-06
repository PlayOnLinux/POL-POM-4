#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python
import subprocess, os, time, threading
from lib.Context import Context

from lib.ConfigFile import GlobalConfigFile 
from lib.ConfigFile import CustomConfigFile
from lib.ConfigFile import UserConfigFile

from lib.Environement import Environement

class ErrExecutableIsRunning(Exception):
   def __str__(self):
      return repr(_("The process is running"))

class ErrExecutableIsNotRunning(Exception):
   def __str__(self):
      return repr(_("The process is not running"))
      
class Executable(threading.Thread):
   def __init__(self, path, args):
      threading.Thread.__init__(self)
      self.pid = 0
      self.path = path[:]
      self.args = args[:]  
      self.execEnv = Environement()
      self.setEnv()
      self.retcode = None
      self.waitingStart = True # Avoid synchronisation problems
      self.running = False
      self.keepAlive = False
      
   def setKeepAlive(self, value = True):
       self.keepAlive = value
       
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

      
    
   # These two methods run the script and return the exitcode
   def parseScriptOut(self, line):
       # This method is made to be overwritten
       return
       
   def run(self):
      
      process = subprocess.Popen(self.getProgramArray(), bufsize=1, preexec_fn = lambda: os.setpgid(os.getpid(), os.getpid()), stdout = subprocess.PIPE, env = self.execEnv.get())
      self.running = True
      self.process = process
      self.pid = process.pid
      self.waitingStart = False
      
      while(True):
          line = process.stdout.readline()

          self.parseScriptOut(line.replace("\n",""))
          
          self.retcode = process.poll() 
          if(self.retcode is not None):
              break
              
      self.running = False
      
      # Need to be tested
      if(not self.keepAlive):
          del self 
              
   def isRunning(self):
       return self.running
  
   def getRetCode(self):
       if(self.isRunning()):
           raise ErrExecutableIsRunning
       else:
           return self.retcode
 
   def getPid(self):
       if(not self.isRunning()):
           raise ErrExecutableIsNotRunning
       else:
           return self.pid
      
           
   def waitProcessEnd(self):
       while (self.isRunning() or self.waitingStart):
           time.sleep(0.01)
       
       self.waitingStart = True
        
   def __del__(self):
       print "I will destroy "+str(self.pid)+str(self.getProgramArray())
       if(self.pid != 0):
          os.system("kill -9 -"+str(self.pid)+" 2> /dev/null")
          os.system("kill -9 "+str(self.pid)+" 2> /dev/null")