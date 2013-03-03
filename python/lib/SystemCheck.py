#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2011 - Quentin PARIS

import os, wx
from lib.Script import PrivateScript
from lib.Executable import Executable

import subprocess
from lib.Context import Context

class SystemCheck(object):
    
   
   def __init__(self):
      self.context = Context()
      
   def appDie(self):
       os._exit(0)
       
   def isRunAsRoot(self):
       return (os.popen("id -u").read() == "0\n" or os.popen("id -u").read() == "0")
      
   
   def executableFound(self, executableToCheck):
       devnull = open('/dev/null', 'wb')
       
       try:
           which = Executable("which",[executableToCheck])
           return (which.runSilently() == 0)
       except OSError:
           return False

   def singleCheck(self, executable, package = None, fatal = False):
       if not self.executableFound(executable):
           
           if package is not None:
               message = _("{0} cannot find {1} from {2}")
           else:
               message = _("{0} cannot find {1}")
               

           if fatal:
               verdict = _("You need to install it to continue")
           else:
               verdict = _("You should install it to use {0}")

           wx.MessageBox(("%s\n\n%s" % (message, verdict)).format(self.context.getAppName(), executable, package), _("Error"))

           if fatal:
               self.appDie()

   def doOpenGLCheck():
       # 32 bits OpenGL check
       check_gl = PrivateScript("check_gl",["x86"])
       returncode = check_gl.run()
        
       if(self.context.getOS() == "Linux" and returncode != 0):
           wx.MessageBox(_("{0} is unable to find 32bits OpenGL libraries.\n\nYou might encounter problem with your games").format(self.context.getAppName()),_("Error"))
           os.environ["OpenGL32"] = "0"
       else:
           os.environ["OpenGL32"] = "1"

       # 64 bits OpenGL check
       if(self.context.is64bit()):
           check_gl_64 = PrivateScript("check_gl",["amd64"])
           returncode = check_gl_64.run()
           
           if(returncode != 0):
               wx.MessageBox(_("{0} is unable to find 64bits OpenGL libraries.\n\nYou might encounter problem with your games").format(self.context.getAppName()),_("Error"))
               os.environ["OpenGL64"] = "0"
           else:
               os.environ["OpenGL64"] = "1"
               
               
   def doFileSystemCheck(self):
       # Filesystem check
       if(self.context.getOS() == "Linux"):
           returncode = PrivateScript("check_fs").run()
           if(returncode != 0):
               wx.MessageBox(_("Your filesystem might prevent {0} from running correctly.\n\nPlease open {0} in a terminal to get more details").format(self.context.getAppName()),_("Error"))
       
              
   def doFullCheck(self):
       # Run as root ?
       if(self.isRunAsRoot()):
           wx.MessageBox(_("{0} is not supposed to be run as root. Sorry").format(self.context.getAppName()),_("Error"))
           self.appDie()

       # Filesystem and OpenGL check
       if(self.context.getOS() == "Linux"):
           self.doOpenGLCheck()
           self.doFileSystemCheck()
       
       # Other import checks
       self.singleCheck("nc", package="Netcat", fatal = True)
       self.singleCheck("tar", fatal = True)
       self.singleCheck("cabextract", fatal = True)
       self.singleCheck("convert", package="ImageMagick", fatal = True)
       self.singleCheck("wget", package="Wget", fatal = True)
       self.singleCheck("gpg", package="GnuPG", fatal = True)

       if(not self.context.isDebianPackage()):
           self.singleCheck("xterm")
           
       self.singleCheck("gettext.sh", package="gettext")  # gettext-base on Debian
       self.singleCheck("icotool", package="icoutils")
       self.singleCheck("wrestool", package="icoutils")
       self.singleCheck("wine", package="Wine")
       self.singleCheck("unzip", package="InfoZIP")
       self.singleCheck("7z", package="P7ZIP full")  # p7zip-full on Debian
   