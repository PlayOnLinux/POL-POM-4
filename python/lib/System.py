#!/usr/bin/env python
# Copyright (C) 2007-2010 PlayOnLinux Team
# Copyright (C) 2011 - Quentin PARIS

import os

class System(object):
    def __init__(self, context):
        self.context = context
        
    def killRegisteredPids():
        for pid in self.context.getRegisteredPids():
            os.system("kill -9 -"+pid+" 2> /dev/null")
            os.system("kill -9 "+pid+" 2> /dev/null")

  
   