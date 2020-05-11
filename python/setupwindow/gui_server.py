#!/usr/bin/python3
# -*- coding:utf-8 -*-

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

import os
import random
import socket
import string
import _thread as thread
import threading
import time
import wx

from .POL_SetupFrame import POL_SetupFrame


class gui_server(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self._host = '127.0.0.1'
        self._port = 30000
        self._running = True
        # This dictionary will contain every created setup window
        self.parent = parent

    def GenCookie(self, length=20, chars=string.ascii_letters + string.digits):
        return ''.join([random.SystemRandom().choice(chars) for i in range(length)])

    def handler(self, connection, addr):
        self.temp = ""
        while True:
            self.tempc = connection.recv(2048).decode()

            self.temp += self.tempc
            if "\n" in self.tempc:
                break

        self.result = self.interact(self.temp.replace("\n", ""))
        connection.send(self.result.encode())
        try:
            connection.shutdown(1)
            connection.close()
        except:
            pass

    def initServer(self):
        if (self._port >= 30020):
            print(_("Error: Unable to reserve a valid port"))
            wx.MessageBox(_("Error: Unable to reserve a valid port"), os.environ["APPLICATION_TITLE"])
            os._exit(0)

        try:
            self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.acceptor.bind((str(self._host), int(self._port)))
            self.acceptor.listen(10)
            os.environ["POL_PORT"] = str(self._port)
            os.environ["POL_COOKIE"] = self.GenCookie()
        except socket.error as msg:
            self._port += 1
            self.initServer()

    def closeServer(self):
        self.acceptor.close()
        self._running = False

    def waitRelease(self, pid):
        result = False
        while (result == False):
            # try:
            if pid in self.parent.windowList:
                try:
                    result = self.parent.windowList[pid].getResult()
                except:
                    break
            else:
                break

            time.sleep(0.1)

        return result

    def interact(self, recvData):
        self.parent.SetupWindowTimer_SendToGui(recvData)
        time.sleep(
            0.1 + self.parent.SetupWindowTimer_delay / 100.)  # We divide by 100, because parent.SWT_delay is in ms, and we want a 10x faster
        sentData = recvData.split("\t")
        if (len(sentData) > 2):
            gotData = self.waitRelease(sentData[2])
        else:
            gotData = ""

        return (str(gotData))

    def run(self):
        self.initServer()
        self.i = 0

        while self._running:
            try:
                self.connection, self.addr = self.acceptor.accept()
            except socket.error as e:
                if e.errno == 4:  # Interrupted system call
                    continue

            thread.start_new_thread(self.handler, (self.connection, self.addr))
            self.i += 1

## FIXME: To be refactored
def readAction(object):
    if (object.SetupWindowTimer_action[0] != os.environ["POL_COOKIE"]):
        print("Bad cookie!")
        object.SetupWindowTimer_action = None
        return False

    object.SetupWindowTimer_action = object.SetupWindowTimer_action[1:]

    if (object.SetupWindowTimer_action[0] == "SimpleMessage"):
        if (len(object.SetupWindowTimer_action) == 2):
            wx.MessageBox(object.SetupWindowTimer_action[1], os.environ["APPLICATION_TITLE"])
            object.SetupWindowTimer_action = None
            return False

    if (object.SetupWindowTimer_action[0] == "POL_Die"):
        if (len(object.SetupWindowTimer_action) == 1):
            object.POLDie()
            object.SetupWindowTimer_action = None
            return False

    if (object.SetupWindowTimer_action[0] == "POL_Restart"):
        if (len(object.SetupWindowTimer_action) == 1):
            object.POLRestart()
            object.SetupWindowTimer_action = None
            return False

    if (object.SetupWindowTimer_action[0] == 'POL_System_RegisterPID'):
        if (len(object.SetupWindowTimer_action) == 2):
            object.registeredPid.append(int(object.SetupWindowTimer_action[1]))
            object.SetupWindowTimer_action = None
            return False

    if (len(object.SetupWindowTimer_action) <= 1):
        object.SetupWindowTimer_action = None
        return False

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_Init'):
        if (len(object.SetupWindowTimer_action) == 5):
            object.windowList[object.SetupWindowTimer_action[1]] = POL_SetupFrame(object,
                                                                                  os.environ["APPLICATION_TITLE"],
                                                                                  object.SetupWindowTimer_action[1],
                                                                                  object.SetupWindowTimer_action[2],
                                                                                  object.SetupWindowTimer_action[3],
                                                                                  object.SetupWindowTimer_action[4])
            object.windowList[object.SetupWindowTimer_action[1]].Center(wx.BOTH)
            object.windowList[object.SetupWindowTimer_action[1]].Show(True)
            object.windowOpened += 1
    else:
        if (object.SetupWindowTimer_action[1] not in object.windowList):
            print(_("WARNING. Please use POL_SetupWindow_Init first"))
            object.SetupWindowTimer_action = None
            return False

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_message'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_message(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_SetID'):
        if (len(object.SetupWindowTimer_action) == 3):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_SetID(
                object.SetupWindowTimer_action[2])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_UnsetID'):
        if (len(object.SetupWindowTimer_action) == 2):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_UnsetID()

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_DebugInit'):
        if (len(object.SetupWindowTimer_action) == 3):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_DebugInit(
                object.SetupWindowTimer_action[2])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_shortcut_list'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_shortcut_list(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_prefix_selector'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_prefix_selector(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_pulsebar'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_pulsebar(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_question'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_question(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_wait'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_wait(object.SetupWindowTimer_action[2],
                                                                                      object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_wait_bis'):
        if (len(object.SetupWindowTimer_action) == 7):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_wait_b(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4],
                object.SetupWindowTimer_action[5], object.SetupWindowTimer_action[6])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_free_presentation'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_free_presentation(
                object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[2])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_textbox'):
        if (len(object.SetupWindowTimer_action) == 6):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_textbox(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4],
                object.SetupWindowTimer_action[5])

    if (object.SetupWindowTimer_action[0] == 'POL_Debug'):
        if (len(object.SetupWindowTimer_action) == 5):
            object.windowList[object.SetupWindowTimer_action[1]].POL_Debug(object.SetupWindowTimer_action[2],
                                                                           object.SetupWindowTimer_action[3],
                                                                           object.SetupWindowTimer_action[4])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_textbox_multiline'):
        if (len(object.SetupWindowTimer_action) == 5):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_textbox_multiline(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_browse'):
        if (len(object.SetupWindowTimer_action) == 7):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_browse(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4],
                object.SetupWindowTimer_action[5], object.SetupWindowTimer_action[6])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_download'):
        if (len(object.SetupWindowTimer_action) == 6):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_download(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4],
                object.SetupWindowTimer_action[5])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_Close'):
        if (len(object.SetupWindowTimer_action) == 2):
            object.windowList[object.SetupWindowTimer_action[1]].Destroy()
            del object.windowList[object.SetupWindowTimer_action[1]]
            object.windowOpened -= 1

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_menu'):
        if (len(object.SetupWindowTimer_action) == 6):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_menu(object.SetupWindowTimer_action[2],
                                                                                      object.SetupWindowTimer_action[3],
                                                                                      object.SetupWindowTimer_action[4],
                                                                                      object.SetupWindowTimer_action[5],
                                                                                      False)

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_menu_num'):
        if (len(object.SetupWindowTimer_action) == 6):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_menu(object.SetupWindowTimer_action[2],
                                                                                      object.SetupWindowTimer_action[3],
                                                                                      object.SetupWindowTimer_action[4],
                                                                                      object.SetupWindowTimer_action[5],
                                                                                      True)

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_checkbox_list'):
        if (len(object.SetupWindowTimer_action) == 6):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_checkbox_list(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4],
                object.SetupWindowTimer_action[5])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_icon_menu'):
        if (len(object.SetupWindowTimer_action) == 8):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_icon_menu(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4],
                object.SetupWindowTimer_action[5], object.SetupWindowTimer_action[6], object.SetupWindowTimer_action[7])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_notice'):
        if (len(object.SetupWindowTimer_action) == 4):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_notice(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_licence'):
        if (len(object.SetupWindowTimer_action) == 5):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_licence(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_login'):
        if (len(object.SetupWindowTimer_action) == 5):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_login(
                object.SetupWindowTimer_action[2], object.SetupWindowTimer_action[3], object.SetupWindowTimer_action[4])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_file'):
        if (len(object.SetupWindowTimer_action) == 5):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_file(object.SetupWindowTimer_action[2],
                                                                                      object.SetupWindowTimer_action[3],
                                                                                      object.SetupWindowTimer_action[4])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_pulse'):
        if (len(object.SetupWindowTimer_action) == 3):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_Pulse(
                object.SetupWindowTimer_action[2])

    if (object.SetupWindowTimer_action[0] == 'POL_SetupWindow_set_text'):
        if (len(object.SetupWindowTimer_action) == 3):
            object.windowList[object.SetupWindowTimer_action[1]].POL_SetupWindow_PulseText(
                object.SetupWindowTimer_action[2])

    object.SetupWindowTimer_action = None

