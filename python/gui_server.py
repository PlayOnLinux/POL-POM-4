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

import socket, threading, thread, guiv3 as gui, os, wx, time

class gui_server(threading.Thread):
    def __init__(self, parent): 
        threading.Thread.__init__(self)
        self._host = '127.0.0.1'
        self._port = 30001
        self._running = True
        # This dictionnary will contain every created setup window
        self.parent = parent

    def handler(self, connection, addr):
        self.temp = connection.recv(2048)
        self.result = self.interact(self.temp.replace("\n",""))
        connection.send(self.result)
        connection.shutdown(1)
        connection.close()

    def initServer(self):
        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor.bind ( ( str(self._host), int(self._port) ) )
        self.acceptor.listen(10)
        self.lock = thread.allocate_lock()
       
       
        # We tell bash what server he should connect
        os.environ["POL_PORT"] = str(self._port)

    def closeServer(self):
        self.acceptor.close()
        self._running = False

    def waitRelease(self, pid):
        result = False
        while(result == False):
            try:
                result = self.parent.windowList[pid].getResult()
            except: # Object is destroyed
                break
                time.sleep(0.1) 
        
        return result

    def interact(self, recvData):
       self.parent.SetupWindowTimer_SendToGui(recvData)
       time.sleep(0.5) 
       return(str(self.waitRelease(recvData.split("\t")[1])))

              

    def run(self): 
        self.initServer()
        self.i = 0
     
        while self._running:
            print('Running on port ' + str(self._port) + ' ... ')
            self.connection, self.addr = self.acceptor.accept()
            thread.start_new_thread(self.handler, (self.connection,self.addr))
            self.i += 1
            #channel.close()