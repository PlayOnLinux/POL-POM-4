#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python

from lib.ConfigFile import FiletypeConfigFile
import wx, os

class Version(object):
    def __init__(self, version):
        self.version = version
        
    def lowerThan(self, versionToCompare):
        version1 = string.split(this.version, "-")
        version2 = string.split(versionToCompare, "-")

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
                
    def __str__(self):
        return self.version