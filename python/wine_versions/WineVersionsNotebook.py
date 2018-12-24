import wx

from lib import Variables


## FIXME: Refactor this code later
class WineVersionsNotebook(wx.Notebook):
    def __init__(self, parent):
        self.notebook = wx.Notebook.__init__(self, parent, -1)
        self.images_onglets = wx.ImageList(16, 16)
        self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env + "/etc/onglet/wine.png"))
        self.SetImageList(self.images_onglets)

        self.sizers = {}
        self.imagesapps = {}
        self.imagesapps_i = {}
        self.availableWineVersionsTreeSelector = {}
        self.waitPanel = {}
        self.installedWineVersionsTreeSelector = {}
        self.button_rm = {}
        self.button_in = {}
        self.boxSizers = {}
        self.panels = {}

    def calculateEventDelta(self, arch):
        if (arch == "amd64"):
            return 100
        else:
            return 0

    def _createInstalledWineVersionsPanel(self, arch):
        installedWineVersionsPanel = wx.Panel(self.panels[arch], -1)
        installedWineVersionsSizer = wx.BoxSizer(wx.VERTICAL)
        installedWineVersionsPanel.SetSizer(installedWineVersionsSizer)
        self.boxSizers[arch].Add(installedWineVersionsPanel, 3, wx.EXPAND)
        installedWineVersionsSizer.AddSpacer(10)
        installedWineVersionsSizer.Add(wx.StaticText(installedWineVersionsPanel, -1, _("Installed Wine versions: ")), 0)
        installedWineVersionsSizer.AddSpacer(10)
        self.installedWineVersionsTreeSelector[arch] = wx.TreeCtrl(installedWineVersionsPanel, 107 + self.calculateEventDelta(arch),
                                                                   style=wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | Variables.widget_borders)
        self.installedWineVersionsTreeSelector[arch].SetImageList(self.imagesapps_i[arch])
        self.installedWineVersionsTreeSelector[arch].SetSpacing(0)
        installedWineVersionsSizer.Add(self.installedWineVersionsTreeSelector[arch], 1, wx.EXPAND)
        installedWineVersionsSizer.AddSpacer(10)

    def _createAvailableWineVersionsPanel(self, arch):
        availableWineVersionsPanel = wx.Panel(self.panels[arch] , -1)
        availableWineVersionsSizer = wx.BoxSizer(wx.VERTICAL)
        availableWineVersionsPanel.SetSizer(availableWineVersionsSizer)
        self.boxSizers[arch].Add(availableWineVersionsPanel, 3, wx.EXPAND)
        availableWineVersionsSizer.AddSpacer(10)
        availableWineVersionsSizer.Add(wx.StaticText(availableWineVersionsPanel, -1, _("Available Wine versions: "), (5, 10)), 0)
        availableWineVersionsSizer.AddSpacer(10)
        self.availableWineVersionsTreeSelector[arch] = wx.TreeCtrl(availableWineVersionsPanel, 106 + self.calculateEventDelta(arch),
                                                                   style=wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | Variables.widget_borders,
                                                                   size=(320, 300), pos=(10, 35))
        self.availableWineVersionsTreeSelector[arch].SetImageList(self.imagesapps[arch])
        self.availableWineVersionsTreeSelector[arch].SetSpacing(0)
        availableWineVersionsSizer.Add(self.availableWineVersionsTreeSelector[arch], 1, wx.EXPAND)
        availableWineVersionsSizer.AddSpacer(10)

    def _createButtonPanel(self, arch):
        buttonsPanel = wx.Panel(self.panels[arch] , -1)
        buttonsSizer = wx.BoxSizer(wx.VERTICAL)
        buttonsPanel.SetSizer(buttonsSizer)

        self.button_rm[arch] = wx.Button(buttonsPanel, 108 + self.calculateEventDelta(arch), "<")
        self.button_in[arch] = wx.Button(buttonsPanel, 109 + self.calculateEventDelta(arch), ">")

        buttonsSizer.AddStretchSpacer()
        buttonsSizer.Add(self.button_rm[arch], 0, wx.CENTER)
        buttonsSizer.AddSpacer(10)
        buttonsSizer.Add(self.button_in[arch], 0, wx.CENTER)
        buttonsSizer.AddStretchSpacer()

        self.button_rm[arch].Enable(False)
        self.button_in[arch].Enable(False)

        self.boxSizers[arch].Add(buttonsPanel, 1, wx.EXPAND)

    def liste_versions(self, arch="x86"):
        self.panels[arch] = wx.Panel(self, -1)

        self.boxSizers[arch] = wx.BoxSizer(wx.HORIZONTAL)
        self.panels[arch].SetSizer(self.boxSizers[arch])
        self.imagesapps[arch] = wx.ImageList(22, 22)
        self.imagesapps_i[arch] = wx.ImageList(22, 22)

        self.boxSizers[arch].AddSpacer(10)
        self._createAvailableWineVersionsPanel(arch)
        self._createButtonPanel(arch)
        self._createInstalledWineVersionsPanel(arch)
        self.boxSizers[arch].AddSpacer(10)

        self.AddPage(self.panels[arch], _("Wine versions") + " (" + arch + ")", imageId=0)
