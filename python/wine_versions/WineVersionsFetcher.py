import json
import os
import threading
import time
import urllib.request
import natsort

from lib import Variables
from wine_versions.WineVersionsTools import fetchUserOS

class WineVersionFetcher(threading.Thread):
    def __init__(self, arch="x86"):
        threading.Thread.__init__(self)
        self.thread_message = "#WAIT#"
        self.versions = []
        self.architecture = arch
        self.start()

    def download(self, game):
        self.getDescription = game

    def run(self):
        self.thread_running = True
        while(self.thread_running):
            if(self.thread_message == "get"):
                try :
                    url = os.environ["WINE_SITE"]
                    wfolder = "-".join([fetchUserOS(), self.architecture])


                    req = urllib.request.Request(url, None, {'User-Agent': Variables.userAgent})
                    handle = urllib.request.urlopen(req, timeout = 5)
                    time.sleep(1)
                    available_distributions = json.loads(handle.read())
                    self.versions_ = []
                    for distribution in available_distributions:
                        if(distribution["name"] == "-".join(["upstream", fetchUserOS(), self.architecture])):
                            for package in distribution["packages"]:
                                version = package["version"]
                                packageUrl = package["url"]
                                sha1sum = package["sha1sum"]
                                if(not os.path.exists(Variables.playonlinux_rep+"/wine/"+wfolder+"/"+version)):
                                    self.versions_.append(version)
                                else:
                                    print("Directory: %s exists" % (Variables.playonlinux_rep+"/wine/"+wfolder+"/"+version))
                        elif(distribution["name"] == "-".join(["staging", fetchUserOS(), self.architecture])):
                            for package in distribution["packages"]:
                                version = package["version"]
                                if(not os.path.exists(Variables.playonlinux_rep+"/wine/"+wfolder+"/"+version+"-staging")):
                                    self.versions_.append(version+"-staging")
                                else:
                                    print("Directory: %s exists" % (Variables.playonlinux_rep+"/wine/"+wfolder+"/"+version+"-staging"))
                        else:
                            print(distribution["name"] + " does not match")

                    self.versions_.sort(key=natsort.natsort_keygen())
                    self.versions_.reverse()
                    self.versions = self.versions_[:]
                    self.thread_message = "Ok"
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    self.thread_message = "Err"
                    self.versions = ["Wine packages website is unavailable"]

            else:
                time.sleep(0.2)
