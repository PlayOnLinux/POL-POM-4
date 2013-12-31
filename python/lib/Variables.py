#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2011 - Quentin PARIS

import os, random, sys, string
import wx, lib.playonlinux as playonlinux

# Un ptit check
try :
    os.environ["POL_OS"]
except :
    print "ERROR ! Please define POL_OS environment var first."
    os._exit(1)

# Variables mixte 1
os.environ["POL_PORT"] = "0"
os.environ["PLAYONLINUX"] = os.path.realpath(os.path.realpath(__file__)+"/../../../")
os.environ["SITE"] = "http://repository.playonlinux.com"
os.environ["VERSION"] = "4.2.2"
os.environ["POL_ID"] = str(random.randint(1,100000000))
os.environ["WINE_SITE"] = "http://www.playonlinux.com/wine/binaries"
os.environ["GECKO_SITE"] = "http://www.playonlinux.com/wine/gecko"
os.environ["MONO_SITE"] = "http://www.playonlinux.com/wine/mono"
homedir = os.environ["HOME"]

# Debian packagers should switch this to TRUE
# It will disable update alerts, bug reports, statistics
# It will set the good locale directory, and it will use the good msttcorefonts
os.environ["DEBIAN_PACKAGE"] = "FALSE"

# Variables PlayOnMac
if (os.environ["POL_OS"] == "Mac"):
    os.environ["PLAYONMAC"] = os.environ["PLAYONLINUX"]
    os.environ["REPERTOIRE"] = os.environ["HOME"]+"/Library/PlayOnMac/"
    os.environ["APPLICATION_TITLE"] = "PlayOnMac"
    os.environ["POL_DNS"] = "playonmac.com"
    windows_add_size = 20;
    windows_add_playonmac = 1;
    widget_borders = wx.SIMPLE_BORDER
    os_name = "darwin"
    os.environ["POL_WGET"] = "wget --prefer-family=IPv4 -q"

# Variables PlayOnLinux
if (os.environ["POL_OS"] == "Linux"):
    os.environ["REPERTOIRE"] = os.environ["HOME"]+"/.PlayOnLinux/"
    os.environ["APPLICATION_TITLE"] = "PlayOnLinux"
    os.environ["POL_DNS"] = "playonlinux.com"
    windows_add_size = 0;
    windows_add_playonmac = 0;
    widget_borders = wx.RAISED_BORDER
    os_name = "linux"
    if not os.path.exists("/proc/net/if_inet6"):
        os.environ["POL_WGET"] = "wget -q"
    else:
        os.environ["POL_WGET"] = "wget --prefer-family=IPv4 -q"

os.environ["POL_CURL"] = "curl"

archi = string.split(os.environ["MACHTYPE"],"-")
archi = archi[0]

if(archi == "x86_64" and os.environ["POL_OS"] == "Linux"):
    os.environ["AMD64_COMPATIBLE"] = "True"
else:
    os.environ["AMD64_COMPATIBLE"] = "False"

# Variables mixtes
os.environ["POL_USER_ROOT"] = os.environ["REPERTOIRE"]
os.environ["TITRE"] = os.environ["APPLICATION_TITLE"]
os.environ["WINEPREFIX"] = os.environ["REPERTOIRE"]+"/wineprefix/default"
os.environ["OS_NAME"] = os_name

# Wine
os.environ["WINEDLLOVERRIDES"] = "winemenubuilder.exe=d"

# Si DYLD_LIBRARY_PATH n'existe pas, on la defini pour etre sur
try :
    os.environ["DYLD_LIBRARY_PATH"]
except:
    os.environ["DYLD_LIBRARY_PATH"] = ""

# Pareil pour LD
try :
    os.environ["LD_LIBRARY_PATH"]
except:
    os.environ["LD_LIBRARY_PATH"] = ""




if (os.environ["POL_OS"] == "Mac"):
    os.environ["MAGICK_HOME"] = os.environ["PLAYONLINUX"]+"/../unix/image_magick/"

    os.environ["PATH"] = os.environ["PLAYONLINUX"]+"/../unix/wine/bin:" + os.environ["PLAYONLINUX"]+"/../unix/image_magick/bin:" + os.environ["PLAYONLINUX"]+"/../unix/tools/bin/:" + os.environ["PATH"]

    os.environ["LD_LIBRARY_PATH"] =  os.environ["PLAYONLINUX"]+"/../unix/wine/lib/:"  + os.environ["PLAYONLINUX"]+"/../unix/image_magick/lib:"+ os.environ["PLAYONLINUX"]+"/../unix/tools/lib/ld:/usr/X11/lib/:" + os.environ["LD_LIBRARY_PATH"]

    os.environ["DYLD_LIBRARY_PATH"] = os.environ["PLAYONLINUX"]+"/../unix/tools/lib/dyld:" + os.environ["PLAYONLINUX"]+"/../unix/image_magick/lib:"+ os.environ["DYLD_LIBRARY_PATH"]
else:
    # Debian maintainer decided for some reason not to let wineserver binary into PATH...
    for winepath in ('/usr/lib/wine', '/usr/lib/wine-unstable', \
                     '/usr/lib/i386-linux-gnu/wine', '/usr/lib/i386-linux-gnu/wine-unstable', \
                     '/usr/lib32/wine', '/usr/lib32/wine-unstable'):
        if os.path.exists('%s/wineserver' % (winepath,)):
            os.environ["PATH"] += ':%s' % (winepath,)
            break

os.environ["PATH_ORIGIN"] = os.environ["PATH"]
os.environ["LD_PATH_ORIGIN"] = os.environ["LD_LIBRARY_PATH"]
os.environ["DYLDPATH_ORIGIN"] = os.environ["DYLD_LIBRARY_PATH"]

playonlinux_env = os.environ["PLAYONLINUX"]
playonlinux_rep = os.environ["REPERTOIRE"]
version = os.environ["VERSION"]
current_user = os.environ["USER"]

os.environ["WGETRC"] = os.environ["POL_USER_ROOT"]+"/configurations/wgetrc"

## Proxy settings
if(playonlinux.GetSettings("PROXY_ENABLED") == "1"):
    if(playonlinux.GetSettings("PROXY_URL") != ""):
        if(playonlinux.GetSettings("PROXY_LOGIN") == ""):
            http_proxy = "http://"+playonlinux.GetSettings("PROXY_URL")+":"+playonlinux.GetSettings("PROXY_PORT")
        else:
            http_proxy = "http://"+playonlinux.GetSettings("PROXY_LOGIN")+":"+playonlinux.GetSettings("PROXY_PASSWORD")+"@"+playonlinux.GetSettings("PROXY_URL")+":"+playonlinux.GetSettings("PROXY_PORT")
        os.environ["http_proxy"] = http_proxy
