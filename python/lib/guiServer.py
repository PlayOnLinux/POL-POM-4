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

import socket, threading, thread, os, wx, time, random
import string

from lib.Context import Context
from lib.UIHelper import UIHelper
from lib.GuiServerQueue import GuiServerQueue

class GuiServer(threading.Thread):
    instance = None    
   
    def __new__(myClass):
        if(myClass.instance is None):
            myClass.instance = object.__new__(myClass)
        return myClass.instance
        
    def __init__(self): 
        try: 
            self.alreadyInit
            
        except AttributeError:
            self.alreadyInit = True
            threading.Thread.__init__(self)
            
            self.host = '127.0.0.1'
            self.runningPort = 0
            self.tryingPort = 30000
        
            self._running = True
            self.cookie = None
            self.queue = GuiServerQueue()
       
    def getQueue(self):
        return self.queue
             
    def setMainWindow(self, window):
        self.mainWindow = window
            
    def getRunningPort(self):
        return self.runningPort
        
    def setRunningPort(self, port):
        self.runningPort = port   
        
    def incRunningPort(self):
        self.runningPort += 1;
        
    def incTryingPort(self):
        self.tryingPort += 1;
        
    def successRunServer(self):
        self.runningPort = self.tryingPort

    def getCookie(self):
        return self.GenCookie()

    def isServerRunning(self):
        return self.runningPort != 0
        
    def waitForServer(self):
        i = 0
        
        while(not self.isServerRunning()):
            time.sleep(0.01)
            if(i >= 300):
                Error('[APP] is not able to start [APP] Setup Window server.')
                os._exit(0)
                break
            i+=1
            
    def GenCookie(self, length=20, chars=string.letters + string.digits):
        if(self.cookie == None):
            self.cookie = ''.join([random.SystemRandom().choice(chars) for i in range(length)])
        return self.cookie


           
    def initServer(self):
        if(self.tryingPort  >= 30020):
           print _("Error: Unable to reserve a valid port")
           wx.MessageBox(_("Error: Unable to reserve a valid port"),Context().getAppName())
           os._exit(0)
           
        try:
           self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           self.acceptor.bind ( ( str(self.host), int(self.tryingPort) ) )
           self.acceptor.listen(10)
           self.successRunServer()
           
        except socket.error, msg:       
           self.incTryingPort()
           self.initServer()
        

    def closeServer(self):
        self.acceptor.close()
        self._running = False

    def waitRelease(self, pid):
        result = False
        while(result == False):
            
            if pid in self.mainWindow.windowList:
                result = self.mainWindow.windowList[pid].getResult()
                
            else:
                break
            
            
            time.sleep(0.1) 
        
        return result

    def interact(self, recvData):
       recvData = recvData.split("\t")
       
       if(recvData[0] != self.getCookie()):
           print "Bad cookie!"
           return ""

       recvData = recvData[1:]
       self.queue.add(recvData)

       if(len(recvData) > 2):
           gotData = str(self.waitRelease(recvData[2]))
       else:
           gotData = ""

       return(gotData)


    
    def handler(self, connection, addr):
        self.temp = "";
        while True:
            self.tempc = connection.recv(2048);
           
            self.temp += self.tempc
            if "\n" in self.tempc:
                break;

        self.result = self.interact(self.temp.replace("\n",""))
        connection.send(self.result)
        
        try: 
           connection.shutdown(1)
           connection.close()
        except:
           pass
               
    def run(self): 
        self.initServer()
        while self._running:
            self.connection, self.addr = self.acceptor.accept()
            thread.start_new_thread(self.handler, (self.connection,self.addr))

        
        
        
        """
        if(data[0] == "SimpleMessage"):
            if(len(data) == 2):
                wx.MessageBox(data[1],Context().getAppName())
                return False 

        if(data[0] == "POL_Die"):
            if(len(data) == 1):
                object.POLDie()            
                return False  

        if(data[0] == "POL_Restart"):
            if(len(data) == 1):
                object.POLRestart()            
                return False  

        if(data[0] == 'POL_System_RegisterPID'):
            if(len(data) == 2):
                Context().registeredPid.append(data[1])
                return False  

        if(len(data) <= 1):
            data = None
            return False

        if(data[0] == 'POL_SetupWindow_Init'):
            if(len(data) == 5):
                #self.mainWindow.windowList[data[1]] = SetupWindow(Context().getAppName(),data[1],data[2],data[3],data[4])
                #self.mainWindow.windowList[data[1]].Center(wx.BOTH)
                #self.mainWindow.windowList[data[1]].Show(True)
                self.mainWindow.createSetupWindow()
                Context().incWindowOpened()
        else:
            if(data[1] not in self.mainWindow.windowList):
                print(_("WARNING. Please use POL_SetupWindow_Init first"))
                return False 
    
        if(data[0] == 'POL_SetupWindow_message'):
            if(len(data) == 4):
                object.windowList[data[1]].POL_SetupWindow_message(data[2],data[3])

        if(data[0] == 'POL_SetupWindow_SetID'):
            if(len(data) == 3):
                object.windowList[data[1]].POL_SetupWindow_SetID(data[2])

        if(data[0] == 'POL_SetupWindow_UnsetID'):
            if(len(data) == 2):
                object.windowList[data[1]].POL_SetupWindow_UnsetID()

        if(data[0] == 'POL_SetupWindow_shortcut_list'):
            if(len(data) == 4):
                object.windowList[data[1]].POL_SetupWindow_shortcut_list(data[2],data[3])
             
        if(data[0] == 'POL_SetupWindow_prefix_selector'):
            if(len(data) == 4):
                object.windowList[data[1]].POL_SetupWindow_prefix_selector(data[2],data[3])
   
        if(data[0] == 'POL_SetupWindow_pulsebar'):
            if(len(data) == 4):
                object.windowList[data[1]].POL_SetupWindow_pulsebar(data[2],data[3])

        if(data[0] == 'POL_SetupWindow_question'):
            if(len(data) == 4):
               object.windowList[data[1]].POL_SetupWindow_question(data[2],data[3])

        if(data[0] == 'POL_SetupWindow_wait'):
           if(len(data) == 4):
               object.windowList[data[1]].POL_SetupWindow_wait(data[2],data[3])

        if(data[0] == 'POL_SetupWindow_wait_bis'):
           if(len(data) == 7):
               object.windowList[data[1]].POL_SetupWindow_wait_b(data[2],data[3],data[4],data[5],data[6])

        if(data[0] == 'POL_SetupWindow_free_presentation'):
           if(len(data) == 4):
               object.windowList[data[1]].POL_SetupWindow_free_presentation(data[3],data[2])

        if(data[0] == 'POL_SetupWindow_textbox'):
           if(len(data) == 5):
               object.windowList[data[1]].POL_SetupWindow_textbox(data[2],data[3],data[4])

        if(data[0] == 'POL_Debug'):
           if(len(data) == 5):
               object.windowList[data[1]].POL_Debug(data[2],data[3],data[4])

        if(data[0] == 'POL_SetupWindow_textbox_multiline'):
           if(len(data) == 5):
               object.windowList[data[1]].POL_SetupWindow_textbox_multiline(data[2],data[3],data[4])

 
        if(data[0] == 'POL_SetupWindow_browse'):
           if(len(data) == 7):
               object.windowList[data[1]].POL_SetupWindow_browse(data[2],data[3],data[4],data[5],data[6])

        if(data[0] == 'POL_SetupWindow_download'):
           if(len(data) == 6):
               object.windowList[data[1]].POL_SetupWindow_download(data[2],data[3],data[4],data[5])

        if(data[0] == 'POL_SetupWindow_Close'):
           if(len(data) == 2):
               object.windowList[data[1]].Destroy()
               del object.windowList[data[1]]
               object.windowOpened -= 1

        if(data[0] == 'POL_SetupWindow_menu'):
           if(len(data) == 6):
               object.windowList[data[1]].POL_SetupWindow_menu(data[2],data[3],data[4],data[5], False)

        if(data[0] == 'POL_SetupWindow_menu_num'):
           if(len(data) == 6):
               object.windowList[data[1]].POL_SetupWindow_menu(data[2],data[3],data[4],data[5], True)
    
        if(data[0] == 'POL_SetupWindow_checkbox_list'):
           if(len(data) == 6):
               object.windowList[data[1]].POL_SetupWindow_checkbox_list(data[2],data[3],data[4],data[5])
    
        if(data[0] == 'POL_SetupWindow_icon_menu'):
           if(len(data) == 8):
               object.windowList[data[1]].POL_SetupWindow_icon_menu(data[2],data[3],data[4],data[5], data[6], data[7])
    
        if(data[0] == 'POL_SetupWindow_licence'):
           if(len(data) == 5):
               object.windowList[data[1]].POL_SetupWindow_licence(data[2],data[3],data[4])
    
        if(data[0] == 'POL_SetupWindow_login'):
           if(len(data) == 5):
               object.windowList[data[1]].POL_SetupWindow_login(data[2],data[3],data[4])
    
        if(data[0] == 'POL_SetupWindow_file'):
           if(len(data) == 5):
               object.windowList[data[1]].POL_SetupWindow_file(data[2],data[3],data[4])
            
        if(data[0] == 'POL_SetupWindow_pulse'):
           if(len(data) == 3):
               object.windowList[data[1]].POL_SetupWindow_Pulse(data[2])
    
        if(data[0] == 'POL_SetupWindow_set_text'):
           if(len(data) == 3):
               object.windowList[data[1]].POL_SetupWindow_PulseText(data[2])
    
        data = None
        """