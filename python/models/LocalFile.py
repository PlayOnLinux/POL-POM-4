#!/usr/bin/env python
# Copyright (C) 2007-2013 PlayOnLinux Team
# Copyright (C) 2013 - Quentin PARIS

# Python

class LocalFile(object):
   def __init__(self, path):
       self.path = path
 
   def getPath(self):
       return self.path
       
   def getFileType(self):
       file_extension = string.split(self.path,".")
       file_extension = file_extension[len(file_extension) - 1]
       return file_extension.lower()
 
    