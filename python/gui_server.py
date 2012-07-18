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
            time.sleep(0.1) ## FIXME
        
        return result

    def interact(self, recvData):
       print recvData
       recvData = recvData.split("\t")

       if(recvData[0] == 'POL_SetupWindow_Init'):
            if(len(recvData) == 5):
                self.parent.windowList[recvData[1]] = gui.POL_SetupFrame(os.environ["APPLICATION_TITLE"],recvData[1],recvData[2],recvData[3],recvData[4])
                self.parent.windowList[recvData[1]].Center(wx.BOTH)
                self.parent.windowList[recvData[1]].Show(True)

       if(recvData[0] == 'POL_SetupWindow_message'):
            if(len(recvData) == 4):
                self.parent.windowList[recvData[1]].POL_SetupWindow_message(recvData[2],recvData[3])
                self.waitRelease(recvData[1])  

       if(recvData[0] == 'POL_SetupWindow_question'):
            if(len(recvData) == 4):
                self.parent.windowList[recvData[1]].POL_SetupWindow_question(recvData[2],recvData[3])
                return(self.waitRelease(recvData[1]))

       if(recvData[0] == 'POL_SetupWindow_wait'):
            if(len(recvData) == 4):
                self.parent.windowList[recvData[1]].POL_SetupWindow_wait(recvData[2],recvData[3])

       if(recvData[0] == 'POL_SetupWindow_wait_bis'):
            if(len(recvData) == 7):
                self.parent.windowList[recvData[1]].POL_SetupWindow_wait_b(recvData[2],recvData[3],recvData[4],recvData[5],recvData[6])

       if(recvData[0] == 'POL_SetupWindow_free_presentation'):
            if(len(recvData) == 4):
                self.parent.windowList[recvData[1]].POL_SetupWindow_free_presentation(recvData[3],recvData[2])
                self.waitRelease(recvData[1])  

       if(recvData[0] == 'POL_SetupWindow_textbox'):
            if(len(recvData) == 5):
                self.parent.windowList[recvData[1]].POL_SetupWindow_textbox(recvData[2],recvData[3],recvData[4])
                return(self.waitRelease(recvData[1]))

       if(recvData[0] == 'POL_SetupWindow_download'):
            if(len(recvData) == 6):
                self.parent.windowList[recvData[1]].POL_SetupWindow_download(recvData[2],recvData[3],recvData[4],recvData[5])
                return(self.waitRelease(recvData[1]))

       if(recvData[0] == 'POL_SetupWindow_Close'):
            if(len(recvData) == 2):
                self.parent.windowList[recvData[1]].Destroy()

       if(recvData[0] == 'POL_SetupWindow_menu'):
            if(len(recvData) == 6):
                self.parent.windowList[recvData[1]].POL_SetupWindow_menu(recvData[2],recvData[3],recvData[4],recvData[5], False)
                return(self.waitRelease(recvData[1]))

       if(recvData[0] == 'POL_SetupWindow_menu_num'):
            if(len(recvData) == 6):
                self.parent.windowList[recvData[1]].POL_SetupWindow_menu(recvData[2],recvData[3],recvData[4],recvData[5], True)
                return(self.waitRelease(recvData[1]))

       return ""

              

    def run(self): 
        self.initServer()
        self.i = 0
     
        while self._running:
            print('Running on port ' + str(self._port) + ' ... ')
            self.connection, self.addr = self.acceptor.accept()
            thread.start_new_thread(self.handler, (self.connection,self.addr))
            self.i += 1
            #channel.close()