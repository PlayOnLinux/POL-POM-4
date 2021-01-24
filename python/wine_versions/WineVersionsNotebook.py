import wx

from lib import Variables

## FIXME: Refactor this code later
from wine_versions.WineVersionsTools import fetch_supported_archs


class WineVersionsNotebook(wx.Notebook):
    def __init__(self, parent):
        self.notebook = wx.Notebook.__init__(self, parent, -1)
        self.images_onglets = wx.ImageList(16, 16)
        self.images_onglets.Add(wx.Bitmap(Variables.playonlinux_env + "/etc/onglet/wine.png"))

        self.SetImageList(self.images_onglets)

        self.sizers = {}
        self.image_list = self._create_image_list()
        self.available_wine_versions_tree_selector = {}
        self.waitPanel = {}
        self.installed_wine_versions_tree_selector = {}
        self.button_uninstall = {}
        self.button_install = {}
        self.boxSizers = {}
        self.panels = {}
        self.available_wine_version_roots = {}
        self.installed_wine_version_roots = {}
        self.number_of_available_versions = {}
        self.number_of_installed_versions = {}
        self.on_install_handler = None
        self.on_remove_handler = None

    def _create_image_list(self):
        image_list = wx.ImageList(22, 22)
        image_list.Add(wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine-packages.png"))
        image_list.Add(wx.Bitmap(Variables.playonlinux_env + "/etc/install/wine-in-use.png"))
        return image_list

    def _calculate_event_number(self, event_id, arch):
        return event_id + list(fetch_supported_archs()).index(arch) * 100

    def _createInstalledWineVersionsPanel(self, architecture):
        installedWineVersionsPanel = wx.Panel(self.panels[architecture], -1)
        installedWineVersionsSizer = wx.BoxSizer(wx.VERTICAL)
        installedWineVersionsPanel.SetSizer(installedWineVersionsSizer)
        self.boxSizers[architecture].Add(installedWineVersionsPanel, 3, wx.EXPAND)
        installedWineVersionsSizer.AddSpacer(10)
        installedWineVersionsSizer.Add(wx.StaticText(installedWineVersionsPanel, -1, _("Installed Wine versions: ")), 0)
        installedWineVersionsSizer.AddSpacer(10)
        self.installed_wine_versions_tree_selector[architecture] = wx.TreeCtrl(installedWineVersionsPanel,
                                                                               self._calculate_event_number(107, architecture),
                                                                               style=wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | Variables.widget_borders)
        self.installed_wine_versions_tree_selector[architecture].SetImageList(self.image_list)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, lambda evt: self._on_select_installed_wine_version(architecture), id=self._calculate_event_number(107, architecture))

        installedWineVersionsSizer.Add(self.installed_wine_versions_tree_selector[architecture], 1, wx.EXPAND)
        installedWineVersionsSizer.AddSpacer(10)

    def _createAvailableWineVersionsPanel(self, architecture):
        availableWineVersionsPanel = wx.Panel(self.panels[architecture], -1)
        availableWineVersionsSizer = wx.BoxSizer(wx.VERTICAL)
        availableWineVersionsPanel.SetSizer(availableWineVersionsSizer)
        self.boxSizers[architecture].Add(availableWineVersionsPanel, 3, wx.EXPAND)
        availableWineVersionsSizer.AddSpacer(10)
        availableWineVersionsSizer.Add(wx.StaticText(availableWineVersionsPanel, -1, _("Available Wine versions: "), (5, 10)), 0)
        availableWineVersionsSizer.AddSpacer(10)
        self.available_wine_versions_tree_selector[architecture] = wx.TreeCtrl(availableWineVersionsPanel,
                                                                               self._calculate_event_number(106, architecture),
                                                                               style=wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | Variables.widget_borders,
                                                                               size=(320, 300), pos=(10, 35))
        self.available_wine_versions_tree_selector[architecture].SetImageList(self.image_list)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, lambda evt: self._on_select_available_wine_version(architecture), id=self._calculate_event_number(106, architecture))

        availableWineVersionsSizer.Add(self.available_wine_versions_tree_selector[architecture], 1, wx.EXPAND)
        availableWineVersionsSizer.AddSpacer(10)

    def _createButtonPanel(self, architecture):
        buttonsPanel = wx.Panel(self.panels[architecture], -1)
        buttonsSizer = wx.BoxSizer(wx.VERTICAL)
        buttonsPanel.SetSizer(buttonsSizer)

        self.button_uninstall[architecture] = wx.Button(buttonsPanel, self._calculate_event_number(108, architecture), "<")
        self.button_install[architecture] = wx.Button(buttonsPanel, self._calculate_event_number(109, architecture), ">")

        buttonsSizer.AddStretchSpacer()
        buttonsSizer.Add(self.button_uninstall[architecture], 0, wx.CENTER)
        buttonsSizer.AddSpacer(10)
        buttonsSizer.Add(self.button_install[architecture], 0, wx.CENTER)
        buttonsSizer.AddStretchSpacer()

        self.button_uninstall[architecture].Enable(False)
        self.button_install[architecture].Enable(False)

        self.Bind(wx.EVT_BUTTON, lambda evt: self._on_delete(architecture), id=self._calculate_event_number(108, architecture))
        self.Bind(wx.EVT_BUTTON, lambda evt: self._on_install(architecture), id=self._calculate_event_number(109, architecture))


        self.boxSizers[architecture].Add(buttonsPanel, 1, wx.EXPAND)

    def add_architecture_tab(self, arch="x86"):
        self.panels[arch] = wx.Panel(self, -1)

        self.boxSizers[arch] = wx.BoxSizer(wx.HORIZONTAL)
        self.panels[arch].SetSizer(self.boxSizers[arch])

        self.boxSizers[arch].AddSpacer(10)
        self._createAvailableWineVersionsPanel(arch)
        self._createButtonPanel(arch)
        self._createInstalledWineVersionsPanel(arch)
        self.boxSizers[arch].AddSpacer(10)

        self.AddPage(self.panels[arch], _("Wine versions") + " (" + arch + ")", imageId=0)

    def clean_version_of_architecture(self, arch):
        self.available_wine_versions_tree_selector[arch].DeleteAllItems()
        self.installed_wine_versions_tree_selector[arch].DeleteAllItems()
        self.available_wine_version_roots[arch] = self.available_wine_versions_tree_selector[arch].AddRoot("")
        self.installed_wine_version_roots[arch] = self.installed_wine_versions_tree_selector[arch].AddRoot("")
        self.number_of_available_versions[arch] = 0
        self.number_of_installed_versions[arch] = 0

    def add_available_version(self, arch, version):
        self.number_of_available_versions[arch] += 1
        self.available_wine_versions_tree_selector[arch].AppendItem(self.available_wine_version_roots[arch], version, 0)

    def add_installed_version(self, arch, version):
        self.number_of_installed_versions[arch] += 1
        self.installed_wine_versions_tree_selector[arch].AppendItem(self.installed_wine_version_roots[arch], version, 0)

    def _on_select_installed_wine_version(self, architecture):
        self.available_wine_versions_tree_selector[architecture].UnselectAll()
        self.button_uninstall[architecture].Enable(True)
        self.button_install[architecture].Enable(False)

    def _on_select_available_wine_version(self, architecture):
        self.installed_wine_versions_tree_selector[architecture].UnselectAll()
        self.button_uninstall[architecture].Enable(False)
        self.button_install[architecture].Enable(True)

    def _on_install(self, architecture):
        selected_version = self.available_wine_versions_tree_selector[architecture].GetItemText(self.available_wine_versions_tree_selector[architecture].GetSelection())
        if self.on_install_handler is not None:
            self.on_install_handler(architecture, selected_version)

    def _on_delete(self, architecture):
        selected_version = self.installed_wine_versions_tree_selector[architecture].GetItemText(self.installed_wine_versions_tree_selector[architecture].GetSelection())
        if self.on_remove_handler is not None:
            self.on_remove_handler(architecture, selected_version)
