import wx

import lib.Variables as Variables

class MiniatureWindow(wx.Frame):
    def __init__(self,parent,id,title,img):
        wx.Frame.__init__(self, parent, -1, title, size = (800, 600+Variables.windows_add_size))
        self.SetIcon(wx.Icon(Variables.playonlinux_env+"/etc/playonlinux.png", wx.BITMAP_TYPE_ANY))
        self.img = wx.StaticBitmap(self, -1, wx.Bitmap(img))
