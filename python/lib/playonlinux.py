#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2010 PlayOnLinux Team

import Variables, os, string


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
	else:
		cfile = Variables.playonlinux_rep+"/wineprefix/"+prefix+"/playonlinux.cfg"
		
	fichier = open(cfile,"r").readlines()
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
	else:
		cfile = Variables.playonlinux_rep+"/wineprefix/"+prefix+"/playonlinux.cfg"

	fichier = open(cfile,"r").readlines()
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
		
	fichier_write = open(cfile,"w")

	i = 0	
	while(i < len(line)): # On ecrit
		fichier_write.write(line[i]+"\n")
		i+=1

def DeleteSettings(setting, prefix='_POL_'):
	if(prefix == "_POL_"):
		cfile = Variables.playonlinux_rep+"/playonlinux.cfg"
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
								
def GetDebugState(game):
	cfile = Variables.playonlinux_rep+"shortcuts/"+game
	try:
		fichier = open(cfile,"r").readlines()
	except:
		return True
	
	for line in fichier:
		line = line.replace("\n","")
		if(line == 'export WINEDEBUG="-all"'):
			return False
		if(line == 'export WINEDEBUG=""'):
			return True
	return False

def SetDebugState(game, state):
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
				line = 'export WINEDEBUG=""'
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
									
def convertVersionToInt(version): # Code par MulX en Bash, adapte en python par Tinou
	#rajouter pour les vesions de dev -> la version stable peut sortir
	#les personnes qui utilise la version de dev sont quand même informé d'une MAJ
	#ex 3.8.1 < 3.8.2-dev < 3.8.2
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
	fichier = open(os.environ["POL_USER_ROOT"]+"/shortcuts/"+shortcut,'r').read()
	fichier = string.split(fichier,"\n")
	i = 0
	while(i < len(fichier)):
		if("WINEPREFIX" in fichier[i]):
			break
		i += 1
	
	try:
		prefix = string.split(fichier[i],"\"")
		prefix = prefix[1].replace("//","/")
		prefix = string.split(prefix,"/")
	
		if(os.environ["POL_OS"] == "Mac"):
			prefix = prefix[6]
		else:
			prefix = prefix[5]
	except:
		prefix = ""
		
	return prefix
	
	
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