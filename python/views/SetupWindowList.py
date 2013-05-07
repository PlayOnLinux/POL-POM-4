#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 PlayOnLinux Team


from models.Observer import Observer

import wx

class SetupWindowList(Observer):
   def __init__(self, controller): 
      Observer.__init__(self)
      self.controller = controller 

   """
   while(not queue.isEmpty()):
       self.doGuiTask(queue.getTask())
       queue.shift()
   
   """
   def doGuiTask(self, data):
       command = data[0]
       scriptPid = data[1]
       
       if(command == "SimpleMessage"):
           Message(data[2])
           GuiServer().getState().release(scriptPid)
           
       if(command == "POL_Die"):
           playOnLinuxApppolDie()
           GuiServer().getState().release(scriptPid)
       
       if(command == "POL_Restart"):
           playOnLinuxApp.polRestart()
           GuiServer().getState().release(scriptPid)   
       
       if(command == 'POL_SetupWindow_Init'):
          if(len(data) == 6):
               isProtected = data[5] == "TRUE"
               self.windowList[scriptPid] = SetupWindow(title = data[2], scriptPid = scriptPid, topImage = data[3], leftImage = data[4], isProtected = isProtected)
               Context().incWindowOpened() 
               GuiServer().getState().release(scriptPid)   
       
   
       if(command == 'POL_SetupWindow_Close'):
           try:
               self.windowList[scriptPid].Destroy()
               GuiServer().getState().release(scriptPid)   
           except KeyError:
               print "Please use POL_SetupWindow_Init first"
          
       
       
       # Other 
       setupWindowCommands = ["POL_SetupWindow_message", "POL_SetupWindow_SetID", "POL_SetupWindow_UnsetID", 
       "POL_SetupWindow_shortcut_list", "POL_SetupWindow_prefix_selector", "POL_SetupWindow_pulsebar", "POL_SetupWindow_question", 
       "POL_SetupWindow_wait", "POL_SetupWindow_wait_bis", "POL_SetupWindow_free_presentation", "POL_SetupWindow_textbox", 
       "POL_SetupWindow_debug", "POL_SetupWindow_textbox_multiline", "POL_SetupWindow_browse", "POL_SetupWindow_download",
       "POL_SetupWindow_menu", "POL_SetupWindow_menu_num", "POL_SetupWindow_checkbox_list", "POL_SetupWindow_icon_menu", "POL_SetupWindow_licence", 
       "POL_SetupWindow_login", "POL_SetupWindow_file", "POL_SetupWindow_pulse", "POL_SetupWindow_set_text"]
       
       if(command in setupWindowCommands):
           
           arguments = data[2:]
           
           try:
               setupWindowObject = self.windowList[scriptPid]
           except KeyError:
               print "Err. Please use POL_SetupWindow_Init first"
               GuiServer().getState().release(scriptPid)  
           else: 
               try:
                   setupWindowFunction = getattr(setupWindowObject, command)
               except AttributeError:
                   Error ('Function not found "%s" (%s)' % (command, arguments) )
               else:
                   try:
                       setupWindowFunction(*arguments)
                   except TypeError, e:
                       print 'Error: %s (%s)' % (e, arguments)
                       
   def notify(self):
       self.controller....