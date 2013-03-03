#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team

from views.Modal import Modal

class Error(Modal):
   def __init__(self, content): 
      self.title = _('Error')
      self.content = content
      self.show()