import threading, time, os, urllib.request
import lib.Variables as Variables

class DescriptionFetcher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.getDescription = ""
        self.getDescription_bis = ""
        self.htmlContent = ""
        self.htmlwait = "###WAIT###"
        self.stars = 0
        self.cat = 0
        self.start()
        self.med_miniature = None
        self.miniature = Variables.playonlinux_env+"/resources/images/pol_min.png"
        self.miniature_defaut = Variables.playonlinux_env+"/resources/images/pol_min.png"

    def download(self, game):
        self.getDescription = game

    def run(self):
        self.thread_running = True
        while(self.thread_running):
            if(self.getDescription == ""):
                time.sleep(0.1)
            else:
                self.htmlContent = self.htmlwait;
                time.sleep(0.5)
                self.getDescription_bis = self.getDescription
                self.med_miniature = None
                self.cut = self.getDescription.split(":")
                if(self.cut[0] == "get"):
                    self.miniature = self.miniature_defaut
                    # Description
                    self.htmlContent = "<font color=red><b>WARNING !</b><br />You are going to execute a non-validated script. <br />This functionality has been added to make script testing easier.<br />It can be dangerous for your computer. <br />PlayOnLinux will NOT be reponsible for any damages.</font>"
                    self.stars = "0"
                else:
                    # Miniatures
                    try :
                        url = os.environ["SITE"]+'/V4_data/repository/screenshot.php?id='+self.getDescription.replace(" ","%20")
                        req = urllib.request.Request(url)
                        handle = urllib.request.urlopen(req)
                        screenshot_id=handle.read()

                        if(screenshot_id != "0"):
                            url_s1 = 'http://www.playonlinux.com/images/apps/min/'+screenshot_id
                            req = urllib.request.Request(url_s1)
                            handle = urllib.request.urlopen(req)

                            open(Variables.playonlinux_rep+"/tmp/min"+screenshot_id,"w").write(handle.read())
                            self.miniature = Variables.playonlinux_rep+"/tmp/min"+screenshot_id

                        else:
                            try:
                                url = os.environ["SITE"]+'/V2_data/miniatures/'+self.getDescription.replace(" ","%20")
                                req = urllib.request.Request(url)
                                handle = urllib.request.urlopen(req)

                                open(Variables.playonlinux_rep+"/tmp/min","w").write(handle.read())
                                self.miniature = Variables.playonlinux_rep+"/tmp/min"
                            except:
                                self.miniature = self.miniature_defaut

                    except :
                        self.miniature = self.miniature_defaut
                        self.med_miniature = None


                    # Description
                    try :
                        url = os.environ["SITE"]+'/V4_data/repository/get_description.php?id='+self.getDescription.replace(" ","%20")
                        req = urllib.request.Request(url)
                        handle = urllib.request.urlopen(req)
                        self.htmlContent = handle.read()
                        if("<i>No description</i>" in self.htmlContent):
                            self.htmlContent = "<i>"+_("No description")+"</i>"
                    except :
                        self.htmlContent = "<i>"+_("No description")+"</i>"

                    if(self.cat == 12):
                        self.htmlContent += "<br /><br /><font color=red><b>WARNING !</b><br />You are going to execute a beta script. <br />This functionality has been added to make script testing easier.<br />It might not work as expected.</font>"

                    try:
                        if(screenshot_id != 0):
                            try:
                                url_s2 = 'http://www.playonlinux.com/images/apps/med/'+screenshot_id
                                req = urllib.request.Request(url_s2)
                                handle = urllib.request.urlopen(req)
                                open(Variables.playonlinux_rep+"/tmp/med"+screenshot_id,"w").write(handle.read())

                                self.med_miniature = Variables.playonlinux_rep+"/tmp/med"+screenshot_id
                            except:
                                self.med_miniature = None
                        else:
                           self.med_miniature = None
                    except:
                        self.med_miniature = None

                    # Stars
                    try :
                        url = os.environ["SITE"]+'/V4_data/repository/stars.php?n='+self.getDescription.replace(" ","%20")
                        req = urllib.request.Request(url)
                        handle = urllib.request.urlopen(req)
                        self.stars = handle.read()
                    except :
                        self.stars = "0"


            if(self.getDescription == self.getDescription_bis):
                self.getDescription = ""
