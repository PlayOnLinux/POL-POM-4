#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2011 - Quentin PARIS

import os

from Context import Context
from lib.GuiServer import GuiServer

class System(object):
    def __init__(self):
        return None
        
    def killRegisteredPids(self):
        self.context = Context()
        for pid in self.context.getRegisteredPids():
            os.system("kill -9 -"+pid+" 2> /dev/null")
            os.system("kill -9 "+pid+" 2> /dev/null")

    # Should not be used alone
    def hardExit(self, code = 0):
        os._exit(code)
   
    def softExit(self, code = 0):
        self.killRegisteredPids()
        GuiServer().closeServer()
        self.hardExit(code)
        
    def polDie(self):
        self.softExit(0)
        
    def polReset(self):
        self.softExit(63)