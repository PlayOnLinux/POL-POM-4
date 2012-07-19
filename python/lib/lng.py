#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import wxversion
import gettext, Variables as Variables, os
import locale, string

class Lang(object):
    def __init__(self):
        return None

class iLang(object):
    def __init__(self):
        if(os.environ["DEBIAN_PACKAGE"] == "TRUE"):
            languages = os.listdir('/usr/share/locale')
        else:
            languages = os.listdir(Variables.playonlinux_env+'/lang/locale')

        langid = wx.LANGUAGE_DEFAULT
        if(os.environ["DEBIAN_PACKAGE"] == "TRUE"):
            localedir = "/usr/share/locale"
        else:
            localedir = os.path.join(Variables.playonlinux_env, "lang/locale")

        domain = "pol"
        mylocale = wx.Locale(langid)
        mylocale.AddCatalogLookupPathPrefix(localedir)
        mylocale.AddCatalog(domain)

        mytranslation = gettext.translation(domain, localedir, [mylocale.GetCanonicalName()], fallback = True)
        mytranslation.install()
