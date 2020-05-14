from lib import Variables


class PackageList:
    def __init__(self):
        self.available_packages = []
        self.loadList()

    def loadList(self):
        try:
            self.available_packages = open(Variables.playonlinux_rep + "/configurations/listes/POL_Functions",
                                           "r").read()
        except IOError as e:  # File does not exits  it will be created when pol is updated
            pass

    def getList(self):
        return self.available_packages

    def getCutList(self):
        clist = self.available_packages.split("\n")
        flist = []
        for key in clist:
            if ("POL_Install" in key):
                flist.append(key)
        return flist

    def getParsedList(self):
        clist = self.getCutList()
        flist = []
        for key in clist:
            flist.append(PackageList.getNameFromPackageLine(key))
        return flist

    def getNameFromId(self, id):
        return self.getParsedList()[id]

    def getPackageFromName(self, selectedPackage):
        broken = False
        for key in self.getCutList():
            key_split = key.split(":")
            try:
                if (key_split[1] == selectedPackage):  # We found it
                    selectedPackage = key_split[0]
                    broken = True
                    break

            except IndexError as e:  # Index error : There is no ':' in the line, so the content of the line is the package we want to install. No need to continue
                broken = True
                break

        if (broken == False):
            selectedPackage = "POL_Install_" + selectedPackage
        return selectedPackage

    @staticmethod
    def getNameFromPackageLine(package):
        try:
            realName = package.split(":")[1].replace("POL_Install_", "")
        except IndexError as e:
            realName = package.replace("POL_Install_", "")
        return realName
