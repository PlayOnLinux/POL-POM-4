#!/usr/bin/python3
# -*- coding: utf-8 -*-

import wx
import gettext, os
from . import Variables
import locale

class Lang(object):
    def __init__(self):
        return None

class iLang(object):
    def __init__(self):
        if(os.environ["DEBIAN_PACKAGE"] == "TRUE"):
            languages = os.listdir('/usr/share/locale')
        else:
            languages = os.listdir(Variables.playonlinux_env+'/lang/locale')

        if(os.environ["POL_OS"] == "Mac"):
            try:
                wxLocale = wx.Locale().FindLanguageInfo(os.environ["RLANG"])

                if wxLocale is not None:
                    langid = wx.Locale().FindLanguageInfo(os.environ["RLANG"]).Language
                else:
                    langid = wx.LANGUAGE_DEFAULT
            except:
                langid = wx.LANGUAGE_DEFAULT 
        else:
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
