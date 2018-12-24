import wx, os
import lib.Variables as Variables

class PlayOnLinuxWindow(wx.Frame):
    def __init__(self, parent, windowId, title = None, size = None, style = wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, windowId, title, size = size, style = style)
        self.SetIcon(wx.Icon(Variables.playonlinux_env + "/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.parent = parent

        if os.environ["POL_OS"] == "Mac":
            self.fontText = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
            self.fontTitle = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
        else :
            self.fontText = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,False, "", wx.FONTENCODING_DEFAULT)
            self.fontTitle = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "", wx.FONTENCODING_DEFAULT)
