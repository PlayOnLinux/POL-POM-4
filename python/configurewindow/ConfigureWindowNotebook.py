import os
import shlex
import subprocess

import wx

from configurewindow.PackageList import PackageList
from lib import playonlinux, Variables, wine


class ConfigureWindowNotebook(wx.Notebook):
    def __init__(self, parent):
        self.packageList = PackageList()
        self.notebook = wx.Notebook.__init__(self, parent, -1)
        self.typing = False
        self.changing_selection = False

    def ChangeTitle(self, new_title):
        self.s_title = new_title
        self.s_prefix = playonlinux.getPrefix(self.s_title)
        self.changing_selection = True
        self.general_elements["name"].SetValue(new_title)
        self.changing = True

    def winebash(self, command, new_env=None):
        args = shlex.split(command)
        if (self.s_isPrefix == True):
            subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/winebash", "--prefix",
                              self.s_prefix] + args, env=new_env)
        else:
            subprocess.Popen(
                ["bash", Variables.playonlinux_env + "/bash/winebash", self.s_title] + args,
                env=new_env)

    def evt_winecfg(self, event):
        self.winebash("winecfg")

    def evt_regedit(self, event):
        self.winebash("regedit")

    def evt_cmd(self, event):
        # http://bugs.winehq.org/show_bug.cgi?id=10063
        new_env = os.environ
        new_env["LANG"] = "C"

        self.winebash("wineconsole cmd", new_env)

    def evt_taskmgr(self, event):
        self.winebash("taskmgr")

    def evt_rep(self, event):
        try:
            os.remove(os.environ["POL_USER_ROOT"] + "/wineprefix/" + self.s_prefix + "/.update-timestamp")
        except:
            pass
        self.winebash("wineboot")

    def evt_wineboot(self, event):
        self.winebash("wineboot")

    def evt_killall(self, event):
        self.winebash("wineserver -k")

    def evt_control(self, event):
        self.winebash("control")

    def evt_config(self, event):
        subprocess.Popen(["bash", Variables.playonlinux_rep + "/configurations/configurators/" + self.s_title])

    def install_package(self, event):
        selectedPackageName = self.Menu.GetItemText(self.Menu.GetSelection())
        if selectedPackageName:
            selectedPackage = self.packageList.getPackageFromName(selectedPackageName)

            if self.s_isPrefix == False:
                subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/installpolpackages",
                                  self.s_title, selectedPackage])
            else:
                subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/installpolpackages", "--prefix",
                                  self.s_prefix, selectedPackage])

    def AddGeneralChamp(self, title, shortname, value, num):
        self.general_elements[shortname + "_text"] = wx.StaticText(self.panelGeneral, -1, title,
                                                                   pos=(15, 19 + num * 40))
        self.general_elements[shortname] = wx.TextCtrl(self.panelGeneral, 200 + num, value, pos=(300, 23 + num * 40),
                                                       size=(250, 20))

    #       self.general_elements[shortname].SetValue(value)

    def AddGeneralElement(self, title, shortname, elements, wine, num):
        if (shortname == "wineversion"):
            elements.insert(0, "System")
            wine.insert(0, "System")
            elemsize = (225, 25)
        else:
            elemsize = (250, 25)

        self.general_elements[shortname + "_text"] = wx.StaticText(self.panelGeneral, -1, title,
                                                                   pos=(15, 19 + num * 40))

        self.general_elements[shortname] = wx.ComboBox(self.panelGeneral, 200 + num, style=wx.CB_READONLY,
                                                       pos=(300, 17 + num * 40), size=elemsize)
        self.general_elements[shortname].AppendItems(elements)
        self.general_elements[shortname].SetValue(elements[0])

        if (shortname == "wineversion"):
            self.addBitmap = wx.Image(Variables.playonlinux_env + "/resources/images/icones/list-add.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            if (os.environ["POL_OS"] == "Linux" or os.environ["POL_OS"] == "FreeBSD"):
                self.general_elements["wineversion_button"] = wx.BitmapButton(self.panelGeneral, 601,
                                                                              pos=(527, 19 + num * 40), size=(21, 21),
                                                                              bitmap=self.addBitmap)
            if (os.environ["POL_OS"] == "Mac"):
                self.general_elements["wineversion_button"] = wx.BitmapButton(self.panelGeneral, 601,
                                                                              pos=(522, 15 + num * 40), size=(21, 21),
                                                                              bitmap=self.addBitmap)

    def General(self, nom):
        self.panelGeneral = wx.Panel(self, -1)
        self.AddPage(self.panelGeneral, nom)
        self.general_elements = {}
        # Les polices
        if (os.environ["POL_OS"] == "Mac"):
            self.fontTitle = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "",
                                     wx.FONTENCODING_DEFAULT)
            self.caption_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "",
                                        wx.FONTENCODING_DEFAULT)
        else:
            self.fontTitle = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "",
                                     wx.FONTENCODING_DEFAULT)
            self.caption_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "",
                                        wx.FONTENCODING_DEFAULT)

        self.txtGeneral = wx.StaticText(self.panelGeneral, -1, _("General"), (10, 10), wx.DefaultSize)
        self.txtGeneral.SetFont(self.fontTitle)

        self.AddGeneralButton(_("Make a new shortcut from this virtual drive"), "newshort", 1)
        self.AddGeneralChamp(_("Name"), "name", "", 2)
        self.AddGeneralElement(_("Wine version"), "wineversion", [], [], 3)
        self.AddGeneralChamp(_("Debug flags"), "winedebug", "", 4)

        self.AddGeneralElement(_("Virtual drive"), "wineprefix", playonlinux.Get_Drives(), playonlinux.Get_Drives(), 5)

        self.AddGeneralChamp(_("Arguments"), "arguments", "", 6)

        self.configurator_title = wx.StaticText(self.panelGeneral, -1, "", (10, 294), wx.DefaultSize)
        self.configurator_title.SetFont(self.fontTitle)
        self.configurator_button = wx.Button(self.panelGeneral, 106, _("Run configuration wizard"), pos=(15, 324))

        self.Bind(wx.EVT_TEXT, self.setname, id=202)
        self.Bind(wx.EVT_TEXT, self.setargs, id=206)
        self.Bind(wx.EVT_TEXT, self.setwinedebug, id=204)

        self.Bind(wx.EVT_COMBOBOX, self.assign, id=203)
        self.Bind(wx.EVT_COMBOBOX, self.assignPrefix, id=205)
        self.Bind(wx.EVT_BUTTON, self.Parent.Parent.Parent.WineVersion, id=601)

    def Wine(self, nom):
        self.panelWine = wx.Panel(self, -1)
        self.AddPage(self.panelWine, nom)
        # Les polices
        self.txtGeneral = wx.StaticText(self.panelWine, -1, "Wine", (10, 10), wx.DefaultSize)
        self.txtGeneral.SetFont(self.fontTitle)

        self.winecfg_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/wine-winecfg.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.winecfg = wx.BitmapButton(self.panelWine, id=100, bitmap=self.winecfg_image, pos=(30, 50),
                                       size=(self.winecfg_image.GetWidth() + 5, self.winecfg_image.GetHeight() + 5))
        self.winecfg_texte = wx.StaticText(self.panelWine, -1, _("Configure Wine"), (32, 156), style=wx.ALIGN_CENTER)
        self.winecfg_texte.Wrap(110)
        self.winecfg_texte.SetPosition((self.winecfg_texte.GetPosition()[0] + (
                    105 - self.winecfg_texte.GetSize()[0]) / 2, self.winecfg_texte.GetPosition()[1]))

        self.winecfg_texte.SetFont(self.caption_font)

        self.regedit_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/registry.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.regedit = wx.BitmapButton(self.panelWine, id=101, bitmap=self.regedit_image, pos=(166, 50),
                                       size=(self.regedit_image.GetWidth() + 5, self.regedit_image.GetHeight() + 5))
        self.regedit_texte = wx.StaticText(self.panelWine, -1, _("Registry Editor"), (168, 156), style=wx.ALIGN_CENTER)
        self.regedit_texte.Wrap(110)
        self.regedit_texte.SetPosition((self.regedit_texte.GetPosition()[0] + (
                    105 - self.regedit_texte.GetSize()[0]) / 2, self.regedit_texte.GetPosition()[1]))

        self.regedit_texte.SetFont(self.caption_font)

        self.wineboot_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/reboot.png",
                                       wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.wineboot = wx.BitmapButton(self.panelWine, id=102, bitmap=self.wineboot_image, pos=(302, 50),
                                        size=(self.wineboot_image.GetWidth() + 5, self.wineboot_image.GetHeight() + 5))
        self.wineboot_texte = wx.StaticText(self.panelWine, -1, _("Windows reboot"), (304, 156), style=wx.ALIGN_CENTER)
        self.wineboot_texte.Wrap(110)
        self.wineboot_texte.SetPosition((self.wineboot_texte.GetPosition()[0] + (
                    105 - self.wineboot_texte.GetSize()[0]) / 2, self.wineboot_texte.GetPosition()[1]))
        self.wineboot_texte.SetFont(self.caption_font)

        self.updatep_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/update.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.updatep = wx.BitmapButton(self.panelWine, id=107, bitmap=self.updatep_image, pos=(438, 50),
                                       size=(self.wineboot_image.GetWidth() + 5, self.updatep_image.GetHeight() + 5))
        self.updatep_texte = wx.StaticText(self.panelWine, -1, _("Repair virtual drive"), (440, 156),
                                           style=wx.ALIGN_CENTER)
        self.updatep_texte.Wrap(110)
        self.updatep_texte.SetPosition((self.updatep_texte.GetPosition()[0] + (
                    105 - self.wineboot_texte.GetSize()[0]) / 2, self.updatep_texte.GetPosition()[1]))
        self.updatep_texte.SetFont(self.caption_font)

        self.cmd_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/console.png",
                                  wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.cmd = wx.BitmapButton(self.panelWine, id=103, bitmap=self.cmd_image, pos=(30, 196),
                                   size=(self.cmd_image.GetWidth() + 5, self.cmd_image.GetHeight() + 5))
        self.cmd_texte = wx.StaticText(self.panelWine, -1, _("Command prompt"), (32, 302), style=wx.ALIGN_CENTER)
        self.cmd_texte.Wrap(110)
        self.cmd_texte.SetPosition((self.cmd_texte.GetPosition()[0] + (105 - self.cmd_texte.GetSize()[0]) / 2,
                                    self.cmd_texte.GetPosition()[1]))
        self.cmd_texte.SetFont(self.caption_font)

        self.taskmgr_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/monitor.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.taskmgr = wx.BitmapButton(self.panelWine, id=104, bitmap=self.taskmgr_image, pos=(166, 196),
                                       size=(self.taskmgr_image.GetWidth() + 5, self.taskmgr_image.GetHeight() + 5))
        self.taskmgr_texte = wx.StaticText(self.panelWine, -1, _("Task manager"), (168, 302), style=wx.ALIGN_CENTER)
        self.taskmgr_texte.Wrap(110)
        self.taskmgr_texte.SetPosition((self.taskmgr_texte.GetPosition()[0] + (
                    105 - self.taskmgr_texte.GetSize()[0]) / 2, self.taskmgr_texte.GetPosition()[1]))

        self.taskmgr_texte.SetFont(self.caption_font)

        self.killall_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/stop.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.killall = wx.BitmapButton(self.panelWine, id=105, bitmap=self.killall_image, pos=(302, 196),
                                       size=(self.killall_image.GetWidth() + 5, self.killall_image.GetHeight() + 5))
        self.killall_texte = wx.StaticText(self.panelWine, -1, _("Kill processes"), (304, 302), style=wx.ALIGN_CENTER)
        self.killall_texte.Wrap(110)
        self.killall_texte.SetPosition((self.killall_texte.GetPosition()[0] + (
                    105 - self.killall_texte.GetSize()[0]) / 2, self.killall_texte.GetPosition()[1]))
        self.killall_texte.SetFont(self.caption_font)

        self.control_image = wx.Image(Variables.playonlinux_env + "/resources/images/configure/control.png",
                                      wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.control = wx.BitmapButton(self.panelWine, id=108, bitmap=self.control_image, pos=(438, 196),
                                       size=(self.control_image.GetWidth() + 5, self.control_image.GetHeight() + 5))
        self.control_texte = wx.StaticText(self.panelWine, -1, _("Control panel"), (440, 302), style=wx.ALIGN_CENTER)
        self.control_texte.Wrap(110)
        self.control_texte.SetPosition((self.control_texte.GetPosition()[0] + (
                    105 - self.control_texte.GetSize()[0]) / 2, self.control_texte.GetPosition()[1]))

        self.control_texte.SetFont(self.caption_font)

        self.Bind(wx.EVT_BUTTON, self.evt_winecfg, id=100)
        self.Bind(wx.EVT_BUTTON, self.evt_regedit, id=101)
        self.Bind(wx.EVT_BUTTON, self.evt_wineboot, id=102)
        self.Bind(wx.EVT_BUTTON, self.evt_cmd, id=103)
        self.Bind(wx.EVT_BUTTON, self.evt_taskmgr, id=104)
        self.Bind(wx.EVT_BUTTON, self.evt_killall, id=105)
        self.Bind(wx.EVT_BUTTON, self.evt_config, id=106)
        self.Bind(wx.EVT_BUTTON, self.evt_rep, id=107)
        self.Bind(wx.EVT_BUTTON, self.evt_control, id=108)

    def Packages(self, nom):
        self.panelPackages = wx.Panel(self, -1)
        self.txtPackages = wx.StaticText(self.panelPackages, -1, _(nom), (10, 10), wx.DefaultSize)
        self.txtPackages.SetFont(self.fontTitle)

        self.imagePackages = wx.ImageList(22, 22)

        self.desPackags = wx.StaticText(self.panelPackages, -1, _(
            "Be careful! Installing one of these components can break your virtual drive."), (10, 40), wx.DefaultSize)

        self.Menu = wx.TreeCtrl(self.panelPackages, 99, pos=(15, 75), size=(530, 260),
                                style=wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | Variables.widget_borders)
        self.Menu.SetSpacing(0);
        self.Menu.SetImageList(self.imagePackages)
        self.imagePackages.RemoveAll()

        self.rootPackages = self.Menu.AddRoot("")
        self.i = 0

        for app in self.packageList.getParsedList():
            self.icon_look_for = Variables.playonlinux_rep + "/configurations/icones/" + self.packageList.getPackageFromName(
                app)
            if (os.path.exists(self.icon_look_for)):
                try:
                    self.imagePackages.Add(wx.Bitmap(self.icon_look_for))
                except:
                    pass
            else:
                self.imagePackages.Add(wx.Bitmap(Variables.playonlinux_env + "/etc/playonlinux22.png"))
            self.Menu.AppendItem(self.rootPackages, app, self.i)
            self.i = self.i + 1

        self.PackageButton = wx.Button(self.panelPackages, 98, _("Install"), pos=(20 + 530 - 150, 345), size=(150, 30))
        self.PackageButton.Disable()

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.package_selected, id=99)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.install_package, id=99)
        self.Bind(wx.EVT_BUTTON, self.install_package, id=98)

        self.AddPage(self.panelPackages, nom)

    def package_selected(self, event):
        selectedPackageName = self.Menu.GetItemText(self.Menu.GetSelection())
        if selectedPackageName:
            self.PackageButton.Enable()
        else:
            self.PackageButton.Disable()

    def change_Direct3D_settings(self, param):
        if (self.s_isPrefix == False):
            subprocess.Popen(
                ["bash", Variables.playonlinux_env + "/bash/POL_Command", self.s_title,
                 "POL_Wine_Direct3D", param, self.display_elements[param].GetValue()])
        else:
            subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command", "--prefix",
                              self.s_prefix, "POL_Wine_Direct3D", param,
                              self.display_elements[param].GetValue()])

    def change_DirectInput_settings(self, param):
        if (self.s_isPrefix == False):
            subprocess.Popen(
                ["bash", Variables.playonlinux_env + "/bash/POL_Command", self.s_title,
                 "POL_Wine_DirectInput", param, self.display_elements[param].GetValue()])
        else:
            subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command", "--prefix",
                              self.s_prefix, "POL_Wine_DirectInput", param,
                              self.display_elements[param].GetValue()])

    def get_current_settings(self, param):
        self.display_elements[param].SetValue(self.settings[param])

    def UpdateVersions(self, arch):
        elements = playonlinux.Get_versions(arch)
        self.general_elements["wineversion"].Clear()
        if (arch == playonlinux.GetSettings("WINE_SYSTEM_ARCH") or (
                arch == "x86" and playonlinux.GetSettings("WINE_SYSTEM_ARCH") != "amd64")):
            self.general_elements["wineversion"].Append("System")
        self.general_elements["wineversion"].AppendItems(elements)
        version = playonlinux.GetSettings('VERSION', self.s_prefix)
        if (version == ''):
            self.general_elements["wineversion"].SetValue('System')
        else:
            self.general_elements["wineversion"].SetValue(version)

    def UpdateValues(self, selection):
        # print "Test"
        if (self.s_isPrefix == False):
            self.ChangeTitle(selection)
            # self.general_elements["wineversion"].SetValue(wine_versions.GetWineVersion(selection))
            # self.general_elements["wineversion"].Show()
            self.general_elements["wineprefix"].Show()
            self.general_elements["arguments"].Show()
            self.general_elements["arguments_text"].Show()

            # self.general_elements["name"].Show()
            # self.general_elements["wineversion_text"].Show()
            self.general_elements["wineprefix_text"].Show()
            self.general_elements["name"].SetEditable(True)

            # self.general_elements["name_text"].Show()
            self.general_elements["wineprefix"].SetValue(playonlinux.getPrefix(self.s_title))
            self.general_elements["arguments"].SetValue(playonlinux.getArgs(self.s_title))

            self.display_elements["folder_button"].SetLabel(_("Open program's directory"))
            if not playonlinux.GetSettings("OPEN_IN", self.s_prefix):
                self.display_elements["open_in"].SetValue("xdg-open")
            else:
                self.display_elements["open_in"].SetValue(playonlinux.GetSettings("OPEN_IN", self.s_prefix))

            if (os.path.exists(Variables.playonlinux_rep + "configurations/configurators/" + self.s_title)):
                self.configurator_title.Show()
                self.configurator_button.Show()
            else:
                self.configurator_title.Hide()
                self.configurator_button.Hide()
            self.configurator_title.SetLabel(
                "{0} specific configuration".format(self.s_title))
            self.display_elements["pre_run_panel"].Show()
            self.display_elements["pre_run_text"].Show()
        else:
            self.s_prefix = selection
            self.s_title = selection
            # self.general_elements["wineversion"].Hide()
            self.general_elements["wineprefix"].Hide()
            # self.general_elements["name"].Hide()
            self.general_elements["name"].SetEditable(False)
            self.general_elements["name"].SetValue(self.s_prefix)
            self.general_elements["arguments"].Hide()
            self.general_elements["arguments_text"].Hide()
            # self.general_elements["wineversion_text"].Hide()
            self.general_elements["wineprefix_text"].Hide()
            # self.general_elements["name_text"].Hide()
            self.display_elements["folder_button"].SetLabel(_("Open virtual drive's directory"))
            self.configurator_title.Hide()
            self.configurator_button.Hide()
            self.display_elements["pre_run_panel"].Hide()
            self.display_elements["pre_run_text"].Hide()

        self.Refresh()
        self.elements = ["UseGLSL", "DirectDrawRenderer", "VideoMemorySize", "OffscreenRenderingMode",
                         "RenderTargetModeLock", "Multisampling", "StrictDrawOrdering", "MouseWarpOverride"]
        self.settings = wine.LoadRegValues(self.s_prefix, self.elements)
        # print self.settings
        self.get_current_settings("UseGLSL")
        self.get_current_settings("DirectDrawRenderer")
        self.get_current_settings("VideoMemorySize")
        self.get_current_settings("OffscreenRenderingMode")
        self.get_current_settings("RenderTargetModeLock")
        self.get_current_settings("Multisampling")
        self.get_current_settings("StrictDrawOrdering")
        self.get_current_settings("MouseWarpOverride")

        self.arch = playonlinux.GetSettings('ARCH', self.s_prefix)
        if (self.arch == ""):
            self.arch = "x86"

        self.UpdateVersions(self.arch)
        self.general_elements["winedebug"].SetValue(playonlinux.GetSettings("WINEDEBUG", self.s_prefix))
        try:
            self.display_elements["pre_run"].SetValue(
                open(os.environ["POL_USER_ROOT"] + "/configurations/pre_shortcut/" + self.s_title, 'r').read())
        except:
            self.display_elements["pre_run"].SetValue("")

    def change_settings(self, event):
        param = event.GetId()
        if (param == 301):
            self.change_Direct3D_settings("UseGLSL")
        if (param == 302):
            self.change_Direct3D_settings("DirectDrawRenderer")
        if (param == 303):
            self.change_Direct3D_settings("VideoMemorySize")
        if (param == 304):
            self.change_Direct3D_settings("OffscreenRenderingMode")
        if (param == 305):
            self.change_Direct3D_settings("RenderTargetModeLock")
        if (param == 306):
            self.change_Direct3D_settings("Multisampling")
        if (param == 307):
            self.change_Direct3D_settings("StrictDrawOrdering")
        if (param == 401):
            self.change_DirectInput_settings("MouseWarpOverride")

    def misc_button(self, event):
        param = event.GetId()
        if (param == 402):
            if (self.s_isPrefix == False):
                playonlinux.open_folder(self.s_title,
                                        self.display_elements["open_in"].GetValue())
            else:
                playonlinux.open_folder_prefix(self.s_prefix)
        if (param == 404):
            if (self.s_isPrefix == False):
                subprocess.Popen(
                    ["bash", Variables.playonlinux_env + "/bash/POL_Command", self.s_title,
                     "POL_OpenShell", self.s_title])
            else:
                subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command", "--prefix",
                                  self.s_prefix, "POL_OpenShell"])

        if (param == 405):
            self.FileDialog = wx.FileDialog(self)
            self.FileDialog.SetDirectory("~")
            self.supported_files = "All|*.exe;*.EXE;*.msi;*.MSI\
            \|Windows executable (*.exe)|*.exe;*.EXE\
            \|Windows install file (*.msi)|*.msi;*MSI"
            self.FileDialog.SetWildcard(self.supported_files)
            self.FileDialog.ShowModal()
            if (self.FileDialog.GetPath() != ""):
                filename = self.FileDialog.GetPath()
                dirname = os.path.dirname(filename)
                if (self.s_isPrefix == True):
                    subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command", "--prefix",
                                      self.s_prefix, "POL_AutoWine", filename], cwd=dirname)
                else:
                    subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command",
                                      self.s_title, "POL_AutoWine", filename], cwd=dirname)

        if (param == 201):
            if (self.s_isPrefix == False):
                subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command", "--init",
                                  self.s_title, "POL_SetupWindow_shortcut_creator"])
            else:
                subprocess.Popen(["bash", Variables.playonlinux_env + "/bash/POL_Command", "--init", "--prefix",
                                  self.s_prefix, "POL_SetupWindow_shortcut_creator"])

    def AddDisplayElement(self, title, shortname, elements, wine, num):
        elements.insert(0, "Default")
        wine.insert(0, "default")
        elemsize = (230, 25)
        self.display_elements[shortname + "_text"] = wx.StaticText(self.panelDisplay, -1, title,
                                                                   pos=(15, 19 + num * 40))

        self.display_elements[shortname] = wx.ComboBox(self.panelDisplay, 300 + num, style=wx.CB_READONLY,
                                                       pos=(300, 17 + num * 40), size=elemsize)
        self.display_elements[shortname].AppendItems(wine)
        self.display_elements[shortname].SetValue(wine[0])
        self.Bind(wx.EVT_COMBOBOX, self.change_settings, id=300 + num)

    def AddMiscElement(self, title, shortname, elements, wine, num):
        elements.insert(0, "Default")
        wine.insert(0, "default")
        elemsize = (230, 25)
        self.display_elements[shortname + "_text"] = wx.StaticText(self.panelMisc, -1, title, pos=(15, 19 + num * 40))

        self.display_elements[shortname] = wx.ComboBox(self.panelMisc, 400 + num, style=wx.CB_READONLY,
                                                       pos=(300, 17 + num * 40), size=elemsize)
        self.display_elements[shortname].AppendItems(wine)
        self.display_elements[shortname].SetValue(wine[0])
        self.Bind(wx.EVT_COMBOBOX, self.change_settings, id=400 + num)

    def AddMiscButton(self, title, shortname, num):
        self.display_elements[shortname + "_button"] = wx.Button(self.panelMisc, 400 + num, "", pos=(15, 19 + num * 40),
                                                                 size=(500, 30))
        self.display_elements[shortname + "_button"].SetLabel(title)

        self.Bind(wx.EVT_BUTTON, self.misc_button, id=400 + num)

    def AddMiscChamp(self, title, shortname, value, num):
        self.display_elements[shortname + "_text"] = wx.StaticText(self.panelMisc, -1, title, pos=(15, 24 + num * 40))
        self.display_elements[shortname] = wx.TextCtrl(self.panelMisc, 400 + num, value, pos=(245, 19 + num * 40),
                                                       size=(270, 25))
        self.Bind(wx.EVT_TEXT, self.set_open_in, id=400 + num)

    def set_open_in(self, event):
        new_open_in = self.display_elements["open_in"].GetValue()
        playonlinux.SetSettings('OPEN_IN', new_open_in, self.s_prefix)

    def AddMiscLongText(self, title, shortname, num):
        self.display_elements[shortname + "_text"] = wx.StaticText(self.panelMisc, -1, title, pos=(15, 19 + num * 40))
        self.display_elements[shortname + "_panel"] = wx.Panel(self.panelMisc, -1, size=wx.Size(450, 70),
                                                               pos=(20, 44 + num * 40))

        try:
            content = open(os.environ["POL_USER_ROOT"] + "/configurations/pre_shortcut/" + self.s_title, 'r').read()
        except:
            content = ""

        self.display_elements[shortname] = wx.TextCtrl(self.display_elements[shortname + "_panel"], 400 + num, content,
                                                       size=wx.Size(448, 68), pos=(2, 2),
                                                       style=Variables.widget_borders | wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.edit_shortcut, id=400 + num)

    def edit_shortcut(self, event):
        content = self.display_elements["pre_run"].GetValue()
        open(os.environ["POL_USER_ROOT"] + "/configurations/pre_shortcut/" + self.s_title, 'w').write(content)

    def AddGeneralButton(self, title, shortname, num):
        self.general_elements[shortname + "_button"] = wx.Button(self.panelGeneral, 200 + num, "",
                                                                 pos=(15, 9 + num * 40), size=(520, 30))
        self.general_elements[shortname + "_button"].SetLabel(title)

        self.Bind(wx.EVT_BUTTON, self.misc_button, id=200 + num)

    def Display(self, nom):
        self.display_elements = {}
        self.panelDisplay = wx.Panel(self, -1)

        self.txtDisplay = wx.StaticText(self.panelDisplay, -1, _(nom), (10, 10), wx.DefaultSize)
        self.txtDisplay.SetFont(self.fontTitle)

        self.AddPage(self.panelDisplay, nom)
        self.AddDisplayElement(_("GLSL Support"), "UseGLSL", ["Enabled", "Disabled"], ["enabled", "disabled"], 1)
        self.AddDisplayElement(_("Direct Draw Renderer"), "DirectDrawRenderer", ["GDI", "OpenGL"], ["gdi", "opengl"], 2)
        self.AddDisplayElement(_("Video memory size"), "VideoMemorySize",
                               ["32", "64", "128", "256", "384", "512", "768", "1024", "2048", "3072", "4096"],
                               ["32", "64", "128", "256", "384", "512", "768", "1024", "2048", "3072", "4096"], 3)
        self.AddDisplayElement(_("Offscreen rendering mode"), "OffscreenRenderingMode",
                               ["fbo", "backbuffer", "pbuffer"], ["fbo", "backbuffer", "pbuffer"], 4)
        self.AddDisplayElement(_("Render target mode lock"), "RenderTargetModeLock",
                               ["disabeld", "readdraw", "readtex"], ["disabled", "readdraw", "readtex"], 5)
        self.AddDisplayElement(_("Multisampling"), "Multisampling", ["Enabled", "Disabled"], ["enabled", "disabled"], 6)
        self.AddDisplayElement(_("Strict Draw Ordering"), "StrictDrawOrdering", ["enabled", "disabled"],
                               ["enabled", "disabled"], 7)

    def Miscellaneous(self, nom):
        self.misc_elements = {}
        self.panelMisc = wx.Panel(self, -1)

        self.txtMisc = wx.StaticText(self.panelMisc, -1, _(nom), (10, 10), wx.DefaultSize)
        self.txtMisc.SetFont(self.fontTitle)

        self.AddMiscElement(_("Mouse warp override"), "MouseWarpOverride", ["Enabled", "Disabled", "Force"],
                            ["enable", "disable", "force"], 1)
        self.AddMiscButton("", "folder", 2)
        self.AddMiscChamp(_("Open directory using command"), "open_in", "", 3)
        self.AddMiscButton(_("Open a shell"), "shell", 4)
        self.AddMiscButton(_("Run a .exe file in this virtual drive"), "exerun", 5)
        self.AddMiscLongText(_("Command to exec before running the program"), "pre_run", 6)

        self.AddPage(self.panelMisc, nom)

    def assign(self, event):
        old_version = playonlinux.GetSettings('VERSION', self.s_prefix)
        if old_version == '':
            old_version = 'System'
        version = self.general_elements["wineversion"].GetValue()
        if version != old_version:
            if (wx.YES == wx.MessageBox(_(
                    "Warning:\n\nAny program still running in this virtual drive will be terminated before Wine version is changed.\nAre you sure you want to continue?"),
                                        os.environ["APPLICATION_TITLE"], style=wx.YES_NO | wx.ICON_QUESTION)):
                self.evt_killall(event)
                if version != 'System':
                    playonlinux.SetSettings('VERSION', version, self.s_prefix)
                else:
                    playonlinux.DeleteSettings('VERSION', self.s_prefix)
            else:
                version = old_version
                self.general_elements["wineversion"].SetValue(old_version)

    def assignPrefix(self, event):
        if (wx.YES == wx.MessageBox(_(
                "Be careful!\nIf you change " + self.s_title + "'s virtual drive, you are likely to break it.\nDo this only if you know what you are doing.\n\nAre you sure you want to continue?"),
                                    os.environ["APPLICATION_TITLE"], style=wx.YES_NO | wx.ICON_QUESTION)):
            drive = self.general_elements["wineprefix"].GetValue()
            playonlinux.SetWinePrefix(self.s_title, drive)
        else:
            self.general_elements["wineprefix"].SetValue(self.s_prefix)

    def ReleaseTyping(self, event):
        self.typing = False

    def setargs(self, event):
        new_args = self.general_elements["arguments"].GetValue()
        playonlinux.writeArgs(self.s_title, new_args)

    def setwinedebug(self, event):
        new_winedebug = self.general_elements["winedebug"].GetValue()
        playonlinux.SetSettings('WINEDEBUG', new_winedebug, self.s_prefix)

    def setname(self, event):
        new_name = self.general_elements["name"].GetValue()
        if (self.changing_selection == False):
            self.typing = True
        else:
            self.changing_selection = False

        if (not os.path.exists(Variables.playonlinux_rep + "shortcuts/" + new_name)):
            try:
                os.rename(Variables.playonlinux_rep + "icones/32/" + self.s_title,
                          Variables.playonlinux_rep + "icones/32/" + new_name)
            except:
                pass

            try:
                os.rename(Variables.playonlinux_rep + "icones/full_size/" + self.s_title,
                          Variables.playonlinux_rep + "icones/full_size/" + new_name)
            except:
                pass

            try:
                os.rename(Variables.playonlinux_rep + "configurations/configurators/" + self.s_title,
                          Variables.playonlinux_rep + "configurations/configurators/" + new_name)
            except:
                pass

            try:
                os.rename(Variables.playonlinux_rep + "shortcuts/" + self.s_title,
                          Variables.playonlinux_rep + "shortcuts/" + new_name)
                self.s_title = new_name
                self.s_prefix = playonlinux.getPrefix(self.s_title)
            except:
                pass

            # if(self.changing == False):
            #       self.Parent.Parent.list_software()
            # else:
            #       self.changing = False
