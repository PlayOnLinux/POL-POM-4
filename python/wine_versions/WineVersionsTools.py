import os

from lib import Variables

def fetchUserOS():
    if (os.environ["POL_OS"] == "Mac"):
        return "darwin"
    elif (os.environ["POL_OS"] == "Linux"):
        return "linux"
    else:
        return "freebsd"

def GetWineVersion(game):
    cfile = Variables.playonlinux_rep + "shortcuts/" + game
    fichier = open(cfile, "r").readlines()
    i = 0
    line = ""
    while (i < len(fichier)):
        fichier[i] = fichier[i].replace("\n", "")
        if ("PATH=" in fichier[i] and "WineVersions" in fichier[i]):
            line = fichier[i].replace("//", "/")
        i += 1

    if line == "":
        version = "System"
    else:
        version = line.replace("PATH=", "").replace("\"", "").replace(Variables.playonlinux_rep, "").replace("//", "/")
        version = version.split("/")
        version = version[1]

    return version
