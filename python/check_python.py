import os, wxversion
print("wxversion(s): " + ", ".join(wxversion.getInstalled()))

if os.environ["POL_OS"] != "Mac":
    wxversion.ensureMinimal('2.8')

import wx
os._exit(0)
