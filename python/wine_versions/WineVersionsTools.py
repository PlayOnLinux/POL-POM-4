import os

from lib import Variables

def fetchUserOS():
    if (os.environ["POL_OS"] == "Mac"):
        return "darwin"
    elif (os.environ["POL_OS"] == "Linux"):
        return "linux"
    else:
        return "freebsd"

def architecture_is_supported(architecture_name):
    return True ## FIXME

def fetch_supported_archs():
    for available_arch in ["x86", "x86on64", "amd64"]:
        if architecture_is_supported(available_arch):
            yield available_arch
