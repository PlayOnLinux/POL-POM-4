import os


def fetchUserOS():
    if (os.environ["POL_OS"] == "Mac"):
        return "darwin"
    elif (os.environ["POL_OS"] == "Linux"):
        return "linux"
    else:
        return "freebsd"


def architecture_is_supported(architecture_name):
    if fetchUserOS() == "linux":
        return architecture_name in ["x86", "amd64"]

    if fetchUserOS() == "darwin":
        if int(os.environ.get("OSX_VERSION", 0)) >= 19:
            return architecture_name in ["x86on64", "amd64"]
        else:
            return architecture_name in ["x86", "amd64"]
    return True ## FIXME

def fetch_supported_archs():
    for available_arch in ["x86", "x86on64", "amd64"]:
        if architecture_is_supported(available_arch):
            yield available_arch
