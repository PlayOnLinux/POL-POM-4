#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2010 PlayOnLinux Team

import Variables, os, string
import shlex, pipes, wx

def winpath(script, path):
    #path=os.path.realpath(path)
    if(path[0] != "/"):
        path=os.environ["WorkingDirectory"]+"/"+path
    path = os.path.realpath(path)
    pref = getPrefix(script)
    ver = GetSettings('VERSION',pref)
    arch = GetSettings('ARCH',pref)
    if(arch == ""):
        arch="x86"
    if(ver == ""):
        return(os.popen("env WINEPREFIX='"+os.environ["POL_USER_ROOT"]+"/wineprefix/"+pref+"/' 'wine' winepath -w '"+path+"'").read().replace("\n","").replace("\r",""))
    else:
        return(os.popen("env WINEPREFIX='"+os.environ["POL_USER_ROOT"]+"/wineprefix/"+pref+"/' '"+os.environ["POL_USER_ROOT"]+"/wine/"+Variables.os_name+"-"+arch+"/"+ver+"/bin/wine' winepath -w '"+path+"'").read().replace("\n","").replace("\r",""))

def open_document(path, ext):
    script = GetSettings(ext, '_EXT_')
    if(script == ""):
        wx.MessageBox(_("There is nothing installed to run .{0} files.").format(ext),os.environ["APPLICATION_TITLE"], wx.OK)
    else:
        try:
            os.system("bash "+Variables.playonlinux_env+"/bash/run_app \""+script.encode("utf-8","replace")+"\" \""+winpath(script.encode("utf-8","replace"),path.encode("utf-8","replace"))+"\"&")
        except:
             os.system("bash "+Variables.playonlinux_env+"/bash/run_app \""+script+"\" \""+winpath(script,path)+"\"&")

def GetWineVersion(game):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    fichier = open(cfile,"r").readlines()
    i = 0
    line = ""
    while(i < len(fichier)):
        fichier[i] = fichier[i].replace("\n","")
        if("PATH=" in fichier[i] and "WineVersions" in fichier[i]):
            line = fichier[i].replace("//","/")
        i += 1

    if(line == ""):
        version = "System"
    else:
        version=line.replace("PATH=","").replace("\"","").replace(Variables.playonlinux_rep,"").replace("//","/")
        version = string.split(version,"/")
        version = version[1]

    return(version)

def GetSettings(setting, prefix='_POL_'):
    if(prefix == "_POL_"):
        cfile = Variables.playonlinux_rep+"/playonlinux.cfg"
    elif(prefix == "_EXT_"):
        cfile = Variables.playonlinux_rep+"/extensions.cfg"
    else:
        cfile = Variables.playonlinux_rep+"/wineprefix/"+prefix+"/playonlinux.cfg"

    try:
        fichier = open(cfile,"r").readlines()
    except:
        return("")

    i = 0
    line = ""
    while(i < len(fichier)):
        fichier[i] = fichier[i].replace("\n","")
        if(setting+"=" in fichier[i]):
            line = fichier[i]
            break
        i += 1
    try:
        line = string.split(line,"=")
        return(line[1])
    except:
        return("")

def SetSettings(setting, value, prefix='_POL_'):
    if(prefix == "_POL_"):
        cfile = Variables.playonlinux_rep+"/playonlinux.cfg"
    elif(prefix == "_EXT_"):
        cfile = Variables.playonlinux_rep+"/extensions.cfg"
    else:
        cfile = Variables.playonlinux_rep+"/wineprefix/"+prefix+"/playonlinux.cfg"

    try:
        fichier = open(cfile,"r").readlines()
    except:
        pass
    else:
        i = 0
        line = []
        found = False
        while(i < len(fichier)):
            fichier[i] = fichier[i].replace("\n","")
            if(setting+"=" in fichier[i]):
                line.append(setting+"="+value)
                found = True
            else:
                line.append(fichier[i])
            i += 1
        if(found == False):
            line.append(setting+"="+value)

        try:
            fichier_write = open(cfile,"w")
        except IOError:
            pass
        else:
            i = 0
            while(i < len(line)): # On ecrit
                fichier_write.write(line[i]+"\n")
                i+=1

def DeleteSettings(setting, prefix='_POL_'):
    if(prefix == "_POL_"):
        cfile = Variables.playonlinux_rep+"/playonlinux.cfg"
    elif(prefix == "_EXT_"):
        cfile = Variables.playonlinux_rep+"/extensions.cfg"
    else:
        cfile = Variables.playonlinux_rep+"/wineprefix/"+prefix+"/playonlinux.cfg"

    fichier = open(cfile,"r").readlines()
    i = 0
    line = []
    found = False
    while(i < len(fichier)):
        fichier[i] = fichier[i].replace("\n","")
        if(setting+"=" not in fichier[i]):
            line.append(fichier[i])
        i += 1

    fichier_write = open(cfile,"w")

    i = 0
    while(i < len(line)): # On ecrit
        fichier_write.write(line[i]+"\n")
        i+=1


def getLog(game):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    try:
        fichier = open(cfile,"r").readlines()
    except:
        return None

    for line in fichier:
        line = line.replace("\n","")
        if('#POL_Log=' in line):
            line = string.split(line,"=")
            return(line[1])
    return None

def GetDebugState(game):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    try:
        fichier = open(cfile,"r").readlines()
    except:
        return True

    for line in fichier:
        line = line.replace("\n","")
        if('export WINEDEBUG=' in line):
            if(line == 'export WINEDEBUG="-all"'):
                return False
            else:
                return True
    return False

def SetDebugState(game, prefix, state):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    try:
        fichier = open(cfile,"r").readlines()
    except:
        return False

    lines = []
    for line in fichier:
        line = line.replace("\n","")
        if('export WINEDEBUG=' in line):
            if(state == True):
                line = 'export WINEDEBUG="%s"' % GetSettings('WINEDEBUG', prefix)
            else:
                line = 'export WINEDEBUG="-all"'
        lines.append(line)

    fichier_write = open(cfile,"w")

    i = 0
    while(i < len(lines)): # On ecrit
        fichier_write.write(lines[i]+"\n")
        i+=1

def keynat(string):
    r'''A natural sort helper function for sort() and sorted()
    without using regular expressions or exceptions.

    >>> items = ('Z', 'a', '10th', '1st', '9')
    >>> sorted(items)
    ['10th', '1st', '9', 'Z', 'a']
    >>> sorted(items, key=keynat)
    ['1st', '9', '10th', 'a', 'Z']

    Borrowed from http://code.activestate.com/recipes/285264/#c6
    by paul clinch.

    License is the PSF Python License, http://www.python.org/psf/license/ (GPL compatible)
    '''
    it = type(1)
    r = []
    for c in string:
        if c.isdigit():
            d = int(c)
            if r and type( r[-1] ) == it:
                r[-1] = r[-1] * 10 + d
            else:
                r.append(d)
        else:
            r.append(c.lower())
    return r

def open_folder(software):
    read = open(Variables.playonlinux_rep+"shortcuts/"+software,"r").readlines()

    if not len(read):
        return

    i = 0;
    while(i < len(read)):
        if("cd \"" in read[i]):
            break
        i += 1

    if len(read) == (i):
        return

    AppDir = read[i][3:]
    if AppDir != "":
        if(os.environ["POL_OS"] == "Mac"):
            os.system("open "+AppDir)
        else:
            os.system("xdg-open "+AppDir)

def open_folder_prefix(software):
    AppDir = os.environ["POL_USER_ROOT"]+"/wineprefix/"+software
    if AppDir != "":
        if(os.environ["POL_OS"] == "Mac"):
            os.system("open "+AppDir)
        else:
            os.system("xdg-open "+AppDir)

def VersionLower(version1, version2):
    version1 = string.split(version1, "-")
    version2 = string.split(version2, "-")

    try:
        if(version1[1] != ""):
            dev1 = True
    except:
        dev1 = False

    try:
        if(version2[1] != ""):
            dev2 = True
    except:
        dev2 = False

    if(version1[0] == version2[0]):
        if(dev1 == True and dev2 == False):
            return True
        else:
            return False

    version1 = [ int(digit) for digit in string.split(version1[0],".") ]
    while len(version1) < 3:
        version1.append(0)

    version2 = [ int(digit) for digit in string.split(version2[0],".") ]
    while len(version2) < 3:
        version2.append(0)

    if(version1[0] < version2[0]):
        return True
    elif(version1[0] == version2[0]):
        if(version1[1] < version2[1]):
            return True
        elif(version1[1] == version2[1]):
            if(version1[2] < version2[2]):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def convertVersionToInt(version): # Code par MulX en Bash, adapte en python par Tinou
    #rajouter pour les vesions de dev -> la version stable peut sortir
    #les personnes qui utilise la version de dev sont quand même informé d'une MAJ
    #ex 3.8.1 < 3.8.2-dev < 3.8.2
    print "Deprecated !"
    if("dev" in version or "beta" in version or "alpha" in version or "rc" in version):
        version = string.split(version,"-")
        version = version[0]
        versionDev = -5
    else:
        versionDev = 0

    version_s = string.split(version,".")
    #on fait des maths partie1 elever au cube et multiplier par 1000
    try:
        versionP1 = int(version_s[0])*int(version_s[0])*int(version_s[0])*1000
    except:
        versionP1 = 0
    try:
        versionP2 = int(version_s[1])*int(version_s[1])*100
    except:
        versionP2 = 0
    try:
        versionP3 = int(version_s[2])*10
    except:
        versionP3 = 0
    return(versionDev + versionP1 + versionP2 + versionP3)

def getPrefix(shortcut): # Get prefix name from shortcut
    if(os.path.isdir(os.environ["POL_USER_ROOT"]+"/shortcuts/"+shortcut)):
        return ""

    fichier = open(os.environ["POL_USER_ROOT"]+"/shortcuts/"+shortcut,'r').read()
    fichier = string.split(fichier,"\n")
    i = 0
    while(i < len(fichier)):
        if("export WINEPREFIX=" in fichier[i]):
            break
        i += 1

    try:
        prefix = string.split(fichier[i],"\"")
        prefix = prefix[1].replace("//","/")
        prefix = string.split(prefix,"/")

        if(os.environ["POL_OS"] == "Mac"):
            index_of_dotPOL = prefix.index("PlayOnMac")
            prefix = prefix[index_of_dotPOL + 2]
        else:
            index_of_dotPOL = prefix.index(".PlayOnLinux")
            prefix = prefix[index_of_dotPOL + 2]
    except:
        prefix = ""

    return prefix


def getArgs(shortcut): # Get prefix name from shortcut
    if(os.path.isdir(os.environ["POL_USER_ROOT"]+"/shortcuts/"+shortcut)):
        return ""

    fichier = open(os.environ["POL_USER_ROOT"]+"/shortcuts/"+shortcut,'r').read()
    fichier = string.split(fichier,"\n")
    i = 0
    while(i < len(fichier)):
        if("POL_Wine " in fichier[i]):
            break
        i += 1

    try:
        args = shlex.split(fichier[i])[2:-1]
        #print args
        args = " ".join([ pipes.quote(x) for x in args])
        #print args
    except:
        args = ""

    return args

def Get_versions(arch='x86'):
    installed_versions = os.listdir(Variables.playonlinux_rep+"/wine/"+Variables.os_name+"-"+arch+"/")
    installed_versions.sort(key=keynat)
    installed_versions.reverse()
    try:
        installed_versions.remove("installed")
    except:
        pass
    return installed_versions

def Get_Drives():
    pref = os.listdir(Variables.playonlinux_rep+"/wineprefix/")
    pref.sort()
    return pref


def SetWinePrefix(game, prefix):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    fichier = open(cfile,"r").readlines()
    i = 0
    line = []
    while(i < len(fichier)): # On retire l'eventuel
        fichier[i] = fichier[i].replace("\n","")
        if("export WINEPREFIX=" not in fichier[i] or "/wineprefix/" not in fichier[i]):
            line.append(fichier[i])
        else:
            line.append("export WINEPREFIX=\""+Variables.playonlinux_rep+"/wineprefix/"+prefix+"\"")
        i += 1

    fichier_write = open(cfile,"w")

    i = 0
    while(i < len(line)): # On ecrit
        fichier_write.write(line[i]+"\n")
        i+=1


def writeArgs(game, args):
    cfile = Variables.playonlinux_rep+"shortcuts/"+game
    fichier = open(cfile,"r").readlines()
    i = 0
    line = []

    while(i < len(fichier)): # On retire l'eventuel
        fichier[i] = fichier[i].replace("\n","")
        if("POL_Wine " not in fichier[i]):
            line.append(fichier[i])
        else:
            try:
                old_string = shlex.split(fichier[i])
                new_string = shlex.split(str(args))
                new_string = old_string[0:2] + new_string
                new_string = " ".join([ pipes.quote(x) for x in new_string])

                new_string = new_string+' "$@"'
                line.append(new_string)
            except:
                line.append(fichier[i])
        i += 1

    fichier_write = open(cfile,"w")
    i = 0
    while(i < len(line)): # On ecrit
        fichier_write.write(line[i]+"\n")
        i+=1

def POL_Open(arg):
    if(os.environ["POL_OS"] == "Mac"):
        os.system("open \""+arg+"\"&")
    else:
        os.system("xdg-open \""+arg+"\"&")

def POL_Error(message):
    wx.MessageBox(message,_("{0} error").format(os.environ["APPLICATION_TITLE"]))
