#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2010 PlayOnLinux Team

from . import Variables
import os


def LoadRegValues(prefix, values):
    cfile = Variables.playonlinux_rep+"wineprefix/"+prefix+"/user.reg"
    result = {}


    for element in values:
        result[element] = "default"

    try:
        fichier = open(cfile,"r").readlines()
    except:
        return result

    for line in fichier:
        line = line.replace("\n","")
        found = False
        for element in values:
            if(element in line):
                line = line.replace("\"","").rstrip("\\0") # workaround for Wine bug #37575
                line = line.split("=")
                line = line[1]
                result[element] = line
                found = True
                break
            #if(found == False):
            #result[element] = "default"
    return(result)
