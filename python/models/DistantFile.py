#!/usr/bin/python
# -*- coding:Utf-8 -*-

# Copyright (C) 2008 Pâris Quentin
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import threading, time, urllib

from patterns.Observable import Observable

class DistantFile(threading.Thread, Observable):
    def __init__(self, url):
        threading.Thread.__init__(self)
        Observable.__init__(self)
        self.url = url
        self.fileSize = 0
        self.blockSize = 0
        self.nbBlocks = 0
        self.finished = False
        self.failed = False

    # Getters
    def getFileSize(self):
        return self.fileSize
  
    def getFileSizeInBytes(self):
        return float(self.fileSize / 1048576.0)

    def getLoadedSizeInBytes(self):
        return float( (self.nbBlocks * self.blockSize) / 1048576.0)
        
    def getBlockSize(self):
        return self.blockSize
        
    def getNbBlocks(self):
        return self.nbBlocks
    
    def getMaxNbBlocks(self):
        return self.getFileSize() / self.getBlockSize()
    
    def isFinished(self):
        return self.finished
        
    def hasFailed(self):
        return self.failed
       
    def waitEnd(self):
        while(not self.finished):
            time.sleep(0.1)

    def download(self, local):
        self.local = local
        self.start()

    def getContent(self):
        self.waitEnd()
        
        if(not self.failed):
            return open(self.local, "r").read()
                       
    # Downloader  
    def _onHook(self, nbBlocks, blockSize, fileSize):
        self.nbBlocks = nbBlocks
        self.blockSize = blockSize
        self.fileSize = fileSize
        
        fileSizeB = float(fileSize / 1048576.0)
        octetsLoadedB = float((nbBlocks * blockSize) / 1048576.0)
        octetsLoadedN = round(octetsLoadedB, 1)
        fileSizeN = round(fileSizeB, 1)
        
        downloadData = {"nbBlocks": nbBlocks, "blockSize": blockSize, "fileSize": fileSize, "fileSizeB" : fileSizeB, "octetsLoadedB" : octetsLoadedB, "octetsLoadedN" : octetsLoadedN, "fileSizeN" : fileSizeN}
        

        
        self.update(data = downloadData)
        
    def _startDownload(self):
        # FIXME, exception need to be explicite
        #try:
        urllib.urlretrieve(self.url, self.local, reporthook = self._onHook)
        #except:
        #    self.failed = True
            
        self.finished = True
 

            
    def run(self):
        self._startDownload()