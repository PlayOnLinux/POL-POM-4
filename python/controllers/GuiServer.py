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

import socket, threading, thread, os, wx, time, random, select, string

import events

class ErrServerIsNotRunning(Exception):
   def __str__(self):
      return repr(_("The server is not running"))

class ErrUnableToStartServer(Exception):
   def __str__(self):
      return repr(_("Unable to start Setup Window server."))

class ErrBadCookie(Exception):
   def __str__(self):
      return repr(_("The cookie received by the script is wrong."))


class GuiServerClientThread(threading.Thread):
   def __init__(self, connection, addr, cookie, app):
      threading.Thread.__init__(self)
      self._cookie = cookie
      self._connection = connection
      self._addr = addr
      self.locked = False
      self.app = app
      
   def run(self):
      data = "";
      while True:
          buff = self._connection.recv(2048);
          data += buff
          if "\n" in buff:
              data = data.replace("\n","")
              break;
      data = data.split("\t")
      
      self._processReceivedData(data)
      self._lock()
      self._connection.shutdown(1)
      self._connection.close()

   def sendData(self, data):
       self._connection.send(data)

   def unlock(self):
       self.locked = False
   
   def _lock(self):
       self.locked = True
       while(self.locked):
           time.sleep(0.1)
           
   def _checkCookie(self, clientCookie):
      if(clientCookie != self._cookie):
         raise ErrBadCookie
           
   def _processReceivedData(self, recvData):
      self._checkCookie(recvData[0])
      recvData = recvData[1:]
      pid = recvData[1]
      
      # Send the event
      evt = events.GuiServerEvent(data = recvData, client = self)
      wx.PostEvent(self.app, evt)
      
      
class GuiServer(threading.Thread):
    def __init__(self, app): 
        threading.Thread.__init__(self)
        self.daemon = True
        self.host = '127.0.0.1'
        self.runningPort = 0
        self.tryingPort = 30000
        self._running = True
        self.cookie = None
        self.app = app
        
    def getRunningPort(self):
        return self.runningPort
        
    def setRunningPort(self, port):
        self.runningPort = port  

    def getCookie(self, length=20, chars=string.letters + string.digits):
        if(self.cookie == None):
            self.cookie = ''.join([random.SystemRandom().choice(chars) for i in range(length)])
        return self.cookie
        
    def isServerRunning(self):
        return self.runningPort != 0
        
    def waitForServer(self):
        i = 0    
        while(not self.isServerRunning()):
            time.sleep(0.01)
            if(i >= 300):
                raise ErrUnableToStartServer
            i+=1
            
  
    def closeServer(self):
        try:
            self.acceptor.close()
        except AttributeError:
            raise ErrServerIsNotRunning
            
        self._running = False
                  
    def _initServer(self):
        if(self.tryingPort  >= 30020):
           print _("Error: Unable to reserve a valid port")
           wx.MessageBox(_("Error: Unable to reserve a valid port"),PlayOnLinux().getAppName())
           os._exit(0)
           
        try:
           self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           self.acceptor.bind ( ( str(self.host), int(self.tryingPort) ) )
           self.acceptor.listen(10)
           self.runningPort = self.tryingPort
           
        except socket.error, msg:       
           self.tryingPort += 1;
           self._initServer()

    def run(self): 
        self._initServer()
        while self._running:        
            connection, addr = self.acceptor.accept()
            client = GuiServerClientThread(connection, addr, self.getCookie(), self.app)
            client.start()
            

        