#!/usr/bin/python
# -*- coding:Utf-8 -*-
import threading
import Variables
import time
import socket
import string
import os, math
import wx
import re
global allowed_people
global refused_people
allowed_people = []
refused_people = []
class IRCClient(threading.Thread):
    string_to_write = ""
    def __init__(self):
        threading.Thread.__init__(self)
        # https://www.freenode.net/irc_servers.shtml
        self.serveur = "chat.freenode.net"
        self.port = 6667
        self.Nick = Variables.current_user+"-pol"
        self.chanAutoJoin = "#playonlinux"
        self.start()
        self.freenode_tried = False

    def get_list(self, chan):
        if(self.ircconnected == True):
            self.connexion.send('NAMES '+chan+'\r\n')

    def htmlspecialchars(self, string):
        self.string = string.replace("<","&lt;")
        self.string = self.string.replace(">","&gt;")
        return self.string

    def _vivify(self, matchobj):
        url = matchobj.group(1)
        return "<A href=\"%s\">%s</A>" % (url, url)

    def urlvivify(self, string):
        return re.sub(r'((?:[fF][tT][pP]://|[hH][tT][tT][pP][sS]?://|[nN][eE][wW][sS]://)[-a-zA-Z0-9._/%?=&#]*)', self._vivify, string, 0)

    def connect(self): # Se connecte au serveur IRC
        if(self.ircconnected == False):
            self.status_messages.append(self.html_convert(None, "Connecting ...","#AA0000","#AA0000",True))
            try:
                self.connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connexion.connect((self.serveur, self.port))
                self.ircconnected = True
                self.connexion.send('NICK' + ' ' + self.Nick + '\r\n')
                self.realname = os.environ["APPLICATION_TITLE"]+" Client "+os.environ["VERSION"]
                self.connexion.send('USER' + ' PlayOnLinux ' + self.Nick + ' ' + self.serveur + ' :' + self.realname + '\r\n')
            except:
                self.status_messages.append(self.html_convert(None, "Error! Unable to connect. Check your internet connexion and try again.","#AA0000","#AA0000",True))
                self.stop()
        else:
            self.status_messages.append(self.html_convert(None, "You are in offline-mode","#AA0000","#AA0000",True))


    def getSettings(self):
        irc_settings = {}

        irc_settings['NICKNAME'] = os.environ["USER"]+"-pol"
        irc_settings['AUTOCONNECT'] = "0"
        irc_settings['ALERT'] = "0"
        irc_settings["PLAYSOUND"] = "1"
        if(os.path.exists(Variables.playonlinux_rep+"/configurations/options/irc")):
            ircfile = open(Variables.playonlinux_rep+"/configurations/options/irc","r").readlines()
            self.i = 0

            while(self.i < len(ircfile)):
                line_parsed = string.split(ircfile[self.i].replace("\n","").replace("\r",""),"=")
                irc_settings[line_parsed[0]] = line_parsed[1]
                self.i += 1
        return irc_settings

    def getNick(self, chaine):
        self.nickname = string.split(chaine, "!")
        self.nickname = self.nickname[0]
        self.nickname = self.nickname[1:len(self.nickname)]
        return self.nickname

    def ChangeNick(self, nick):
        if(self.ircconnected == True):
            self.connexion.send("NICK :"+nick+"\r\n")
            self.Nick = nick


    def GenColor(self, pseudo):
        self.colors = ["000","F00","00F","080","008","010","02E","02F","D60","D80","DA0","E00","E40","E50","E70","E80","F24","F42","777"
                       "06F","090","0A0","0AD","0C0","0F0","0CF","150","209","21F","D11","D12","D13","D20","D40","EA0","F27","F43","666"
                       "280","29E","300","30F","32F","34F","36F","470","560","5A0","5AF","5F0","64F","750","800","850","F28","F44","999"
                       "A90","A80","A00","A0F","A1E","A1C","A08","A70","C40","C30","C60","C80","CA0","D10","EC0","EC1","F29","F45","222"
                       "EC2","EC3","ED1","ED0","ED3","F10","F11","F12","F13","F14","F20","F21","F22","F23","F24","F26","F41","090",
                       "F91","F92","F93","F94","F95","F96","F97","F98","F99","F9A","F9A","F9C","F9D","F9E","F9F","0A0","0A1","0A2",
                       "0D0","0D1","0D2","0D3","0D4","0D5","0D6","0D7","0D8","0D9","0DA","0DA","0DC","0DD","0DE","0DF","FE0","FE1",
                       "FE2","FD0","FD1","FD2","160","161","162","163","164","165","166","170","171","173","174","175","176","#AAA"]
        #self.colors.sort()
        self.colors.reverse()

        i = 0
        somme = 0
        max = 0
        while(i < len(pseudo)):
            i += 1
            somme += ord(pseudo[i - 1])*i
            max += 127*i



        num=math.cos(somme * len(self.colors) / max) * len(self.colors)
        num=int(num)
        #print num
        return "0x"+self.colors[num]

    def smile(self, string):
        self.newstring = string
        self.newstring = self.newstring.replace("O:-)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-angel.png'>")
        self.newstring = self.newstring.replace(":-)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-smile.png'>")
        self.newstring = self.newstring.replace(":)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-smile.png'>")
        self.newstring = self.newstring.replace(":-(","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-sad.png'>")
        self.newstring = self.newstring.replace(":(","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-sad.png'>")
        self.newstring = self.newstring.replace(":'(","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-crying.png'>")
        self.newstring = self.newstring.replace("(6)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-devilish.png'>")
        self.newstring = self.newstring.replace("8-)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-glasses.png'>")
        self.newstring = self.newstring.replace(":-O","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-surprise.png'>")
        self.newstring = self.newstring.replace(":-D","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-grin.png'>")
        self.newstring = self.newstring.replace(":D","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-grin.png'> ")
        self.newstring = self.newstring.replace(":-*","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-kiss.png'>")
        self.newstring = self.newstring.replace("(monkey)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-monkey.png'>")
        self.newstring = self.newstring.replace(":-|","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-plain.png'>")
        self.newstring = self.newstring.replace(":|","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-plain.png'> ")
        self.newstring = self.newstring.replace(";-)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-wink.png'> ")
        self.newstring = self.newstring.replace(";)","<img src='"+Variables.playonlinux_env+"/resources/images/emotes/face-wink.png'> ")
        return self.newstring

    def playsound(self):
        settings = self.getSettings()
        if(settings["PLAYSOUND"] == "1"):
            #os.system("playsound "+Variables.playonlinux_env+"/etc/snd/snd.wav & 2> /dev/null > /dev/null")
            sound = wx.Sound(Variables.playonlinux_env+"/resources/sounds/irc.wav")
            sound.Play(wx.SOUND_SYNC)

    def join(self, chan):
        if(chan.lower() not in self.chans and self.ircconnected == True):
            if(chan[0] == "#"):
                self.connexion.send("JOIN :"+chan+"\r\n")
            self.chans.append(chan.lower())
            self.endnames.append(False)
            self.names.append([])
            self.messages.append([])

        self.select_window = chan.lower()

            #self.open_window.append(chan.lower())
            #self.get_list(chan)

    def leave_chan(self, chan):
        if(chan.lower() in self.chans and self.ircconnected == True):
            index = self.get_index(chan)
            if(chan[0] == "#"):
                self.connexion.send("PART :"+chan+"\r\n")

            del self.messages[index]
            del self.names[index]
            del self.endnames[index]
            del self.chans[index]
            self.select_window = self.chanAutoJoin

    def html_convert(self, pseudo, message, pseudocolor='#000000', messagecolor='#000000', action = False):
        tps = time.strftime("%H:%M:%S")
        message = message.replace("  "," &nbsp;")
        message = message.replace("\x1f","")
        message = message.replace("\x02","")
        message = self.htmlspecialchars(message)
        message = self.urlvivify(message)
        message = self.smile(message)
        if(pseudo != None):
            if(action == False):
                return "<font color='"+pseudocolor+"'>("+tps+") <b>"+pseudo+":</b> </font><font color='"+messagecolor+"'>"+message+"</font>"
            else:
                return "<font color='"+pseudocolor+"'>("+tps+") <b>*** "+pseudo+"</b> </font><font color='"+messagecolor+"'>"+message+"</font>"
        else :
            return "<font color='"+messagecolor+"'>("+tps+") "+message+"</font>"
    def get_index(self, content):
        self.boucle = 0
        while(self.boucle < len(self.chans)):
            if(self.chans[self.boucle].lower() == content):
                return self.boucle
            self.boucle +=1

        return -1

    def getMsg(self, array, num=3):
        self.boucle = num
        self.chaine = ""
        while(self.boucle < len(array)):
            self.chaine += array[self.boucle]+" "
            self.boucle += 1
        return self.chaine[1:len(self.chaine)-1]

    def check_access(self, window, i=0):
        print("Try #"+str(i))
        if(window in allowed_people):
            return True
        elif(window in refused_people):
            return False
        else:
            if(i == 0):
                self.connexion.send("PRIVMSG PlayOnLinux :CHECK_ACCESS "+window+"\r\n")
            if(i <= 5):
                time.sleep(1)
                return self.check_access(window, i+1)
            else:
                return False

    def SendMSG(self, message, chan="~current"):
        if(self.ircconnected == False):
            self.status_messages.append(self.html_convert(None, "You are not connected.","#FF0000","#FF0000",True))
        else :
            if(message[0] == "/"): # Une commande
                self.message_parsed = string.split(message," ")
                if(self.message_parsed[0].lower() == "/join" and len(self.message_parsed) > 1):
                    if(self.message_parsed[1][0] == "#"):
                        newchan = self.message_parsed[1].lower()
                    else:
                        newchan = "#"+self.message_parsed[1].lower()
                    self.join(newchan)

                if(self.message_parsed[0].lower() == "/query" and len(self.message_parsed) > 1):
                    newchan = self.message_parsed[1].lower()
                    self.join(newchan)

                if(self.message_parsed[0].lower() == "/kick" and len(self.message_parsed) > 1):
                    user = self.message_parsed[1].lower()
                    if(len(self.message_parsed) > 2):
                        self.i = 2
                        message = ""
                        while(self.i < len(self.message_parsed)):
                            if(self.i != 2):
                                message += " "
                            message += self.message_parsed[self.i]
                            self.i += 1
                    else :
                        message = self.Nick

                    self.connexion.send("KICK "+self.selected_window+" "+user+" "+message+"\r\n")

                if(self.message_parsed[0].lower() == "/nick" and len(self.message_parsed) > 1):
                    self.ChangeNick(self.message_parsed[1])

                if(self.message_parsed[0].lower() == "/me" and len(self.message_parsed) > 1):
                    if(chan == "~current"):
                        window = self.selected_window
                    else:
                        window = chan
                    self.connexion.send("PRIVMSG "+window+" :\x01ACTION "+message.replace("/me ","")+" \x01\r\n")
                    self.index = self.get_index(window)
                    self.messages[self.index].append(self.html_convert(self.Nick,message.replace("/me ",""),"#000088","#000088",True))

                if((self.message_parsed[0].lower() == "/msg" or self.message_parsed[0].lower() == "/privmsg") and len(self.message_parsed) > 2):
                    self.join(self.message_parsed[1].lower())
                    self.i = 2
                    message = ""

                    while(self.i < len(self.message_parsed)):
                        if(self.i != 2):
                            message += " "
                        message += self.message_parsed[self.i]
                        self.i += 1


                    self.connexion.send("PRIVMSG "+self.message_parsed[1].lower()+" :"+message+"\r\n")
                    self.index = self.get_index(self.message_parsed[1].lower())
                    self.messages[self.index].append(self.html_convert(self.Nick,message,"#000088","#000088",True))

            else:
                if(chan == "~current"):
                    window = self.selected_window
                else:
                    window = chan

                if self.check_access(window):
                    self.connexion.send("PRIVMSG "+window+" :"+message+"\r\n")

                    self.index = self.get_index(window)
                    if(window[0] != "#"):
                        self.messages[self.index].append(self.html_convert(self.Nick,message,"#000088"))
                    else:
                        self.messages[self.index].append(self.html_convert(self.Nick,message,str(self.GenColor(self.Nick)).replace("0x","#")))
                else:
                    wx.MessageBox(_("Sorry, this person does not want to receive private messages").format(os.environ["APPLICATION_TITLE"]),_("Error"))

    def filtrer_liste(self, liste):
        self.boucle = 0
        self.new_list = []
        while(self.boucle < len(liste)):
            self.new_list.append(liste[self.boucle].replace("@","").replace("+","").replace("&","").replace("%","").replace("~","").lower())
            self.boucle += 1

        return self.new_list

    def traiter(self, line):
        if(len(self.names) > 1 and "@PlayOnLinux" not in self.names[1] and self.endnames[1] == True):
            self.status_messages.append(self.html_convert(None, _("Sorry {0} messenger service is not available for the moment.\n\nPlease retry later").format(os.environ["APPLICATION_TITLE"]),"#AA0000","#AA0000",True))
            self.stop()

        self.line = string.split(line, " ") # On parse la ligne mot par mot
        # On répond aux pings
        if(self.line[0] and len(self.line) > 1):
            self.message_id = self.line[1]
            if(self.line[0] == "PING"): # PINGS
                self.connexion.send("PONG "+self.line[1]+"\r\n")



            if(self.message_id == '353'): # NAMES
                if(len(self.line) > 4):
                    self.canal = self.line[4].lower()
                    self.canal_index = self.get_index(self.canal)
                    if(self.canal_index != -1):
                        if(self.endnames[self.canal_index] == True):
                            self.names[self.canal_index] = []
                            self.endnames[self.canal_index] = False

                        self.boucle = 5
            #                       self.names[self.canal_index].append(self.message_id[4])
                        while(self.boucle < len(self.line)):
                            if(self.line[self.boucle] != ''):
                                self.names[self.canal_index].append(self.line[self.boucle].replace(":",""))
                            self.boucle +=1

            if(self.message_id == '366'): # END NAMES
                if(len(self.line) > 3):
                    self.canal = self.line[3].lower()
                    self.canal_index = self.get_index(self.canal)
                    if(self.canal_index != -1):
                        self.endnames[self.canal_index] = True

            if(self.message_id == '001'): # CONNECTED
                self.join(self.chanAutoJoin)

            if(self.message_id == '332'): # topic
                self.subject = self.getMsg(self.line, 4)
                if(len(self.line) > 3):
                    self.chan = self.line[3].lower()
                    self.chan_index = self.get_index(self.chan)
                    self.messages[self.chan_index].append(self.html_convert(None,"Welcome to "+self.chan+"","#666666","#666666",True))
                    self.messages[self.chan_index].append(self.html_convert(None,"The topic is : "+self.subject+"","#666666","#666666",True))

            if(self.message_id == 'TOPIC'):
                if(len(self.line) > 2):
                    self.sender = self.getNick(self.line[0])
                    self.chan = self.line[2].lower()
                    self.subject = self.getMsg(self.line)
                    self.messages[self.chan_index].append(self.html_convert(self.sender," has defined the topic : "+self.subject+"","#666666","#666666",True))

            if(self.message_id == '474'): # Banned
                if(len(self.line) > 3):
                    self.chan = self.line[3].lower()
                    self.chan_index = self.get_index(self.chanAutoJoin)

                    if(self.chan == self.chanAutoJoin):
                        self.status_messages.append(self.html_convert(None,"Unable to join the chat : You have been banned","#AA0000","#AA0000",True))
                        self.stop()
                    else:
                        self.messages[self.chan_index].append(self.html_convert(None,"Unable to join "+self.chan+" : You have been banned","#AA0000","#AA0000",True))
                        self.leave_chan(self.chan)
            #[':irc.steredenn.fr', '474', 'tinou-pol', '#playonlinux', ':Cannot', 'join', 'channel', '(+b)']

            if(self.message_id == 'JOIN'):
                if(len(self.line) > 2):
                    self.sender = self.getNick(self.line[0])
                    self.window = self.line[2].lower().replace(":","")
                    self.index = self.get_index(self.window)
                    message = " has joined "+self.window
                    self.messages[self.index].append(self.html_convert(self.sender,message,"#888888","#888888",True))
                    self.get_list(self.chans[self.index])

            if(self.message_id == 'PART'):
                if(len(self.line) > 2):
                    self.sender = self.getNick(self.line[0])
                    self.window = self.line[2].lower().replace(":","")
                    self.index = self.get_index(self.window)
                    message = " has left "+self.window
                    self.messages[self.index].append(self.html_convert(self.sender,message,"#888888","#888888",True))
                    self.get_list(self.chans[self.index])

            if(self.message_id == '401'): # No such nick channels
                if(len(self.line) > 3):
                    self.msg_to = self.line[3]
                    message = " is offline"
                    self.index = self.get_index(self.msg_to)
                    self.messages[self.index].append(self.html_convert(self.msg_to,message,"#888888","#888888",True))

            if(self.message_id == '482'): # No such nick channels
                message = "Your not channel operator"
                self.index = self.get_index(self.selected_window)
                self.messages[self.index].append(self.html_convert(None,message,"#888888","#888888",True))

            if(self.message_id == 'NICK'):
                if(len(self.line) > 2):
                    self.sender = self.getNick(self.line[0])
                    self.new_nick = self.line[2].replace(":","")
                    message = " is known as "+self.new_nick
                    self.i = 0
                    while(self.i < len(self.chans)):
                        if(self.sender.lower() in self.filtrer_liste(self.names[self.i])):
                            self.messages[self.i].append(self.html_convert(self.sender,message,"#888888","#888888",True))
                            self.get_list(self.chans[self.i])
                        self.i += 1

            if(self.message_id == 'MODE'):
                if(len(self.line) > 3):
                    self.chan = self.line[2].lower()
                    if(len(self.line) > 4):
                        self.victime = self.line[4]
                    else:
                        self.victime = None

                    self.index = self.get_index(self.chan)
                    self.sender = self.getNick(self.line[0])

                    if("+v" in self.line[3] or "-v" in self.line[3]):
                        self.get_list(self.chan)

                    if("+o" in self.line[3]):
                        message = " has given operator acces to "+self.victime
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#AA0000","#AA0000",True))
                        self.get_list(self.chan)

                    if("-o" in self.line[3]):
                        message = " has removed operator acces to "+self.victime
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#AA0000","#AA0000",True))
                        self.get_list(self.chan)

                    if("+h" in self.line[3]):
                        message = " has given half-operator acces to "+self.victime
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#AA0000","#AA0000",True))
                        self.get_list(self.chan)

                    if("-h" in self.line[3]):
                        message = " has removed half-operator acces to "+self.victime
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#AA0000","#AA0000",True))
                        self.get_list(self.chan)

                    if("+b" in self.line[3]):
                        message = " has banned "+self.victime
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#AA0000","#AA0000",True))
                        self.get_list(self.chan)

                    if("-b" in self.line[3]):
                        message = " has unbanned "+self.victime
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#AA0000","#AA0000",True))
                        self.get_list(self.chan)

            if(self.message_id == '433'): # Nick already in use
                self.status_messages.append(self.html_convert(None, "Error : Nickname already in use","#FF0000","#FF0000",True))
                self.stop()

            if(self.message_id == '432'): # Nick contain illegal caracteres
                self.status_messages.append(self.html_convert(None, "Error : Nickname contains illegal characters","#FF0000","#FF0000",True))
                self.stop()

            if(self.line[0] == 'ERROR'): # Nick contain illegal caracteres
                self.stop()

            if(self.message_id == "KICK"):
                if(len(self.line) > 3):
                    self.sender = self.getNick(self.line[0])
                    self.kicked = self.line[3]
                    self.chan = self.line[2].lower()
                    self.index = self.get_index(self.chan)
                    self.raison = self.getMsg(self.line,4)
                    self.chan_index = self.get_index(self.chanAutoJoin)

                    if(self.kicked.lower() == self.Nick.lower()):
                        if(self.chan == self.chanAutoJoin):
                            self.status_messages.append(self.html_convert(self.sender," has kicked you from the chat : "+self.raison,"#FF0000","#FF0000",True))
                            self.stop()
                        else :
                            self.messages[self.chan_index].append(self.html_convert(self.sender," has kicked you from "+self.chan+" : "+self.raison,"#FF0000","#FF0000",True))
                            self.leave_chan(self.chan)
                    else :
                        self.messages[self.index].append(self.html_convert(self.sender," has been kicked "+self.kicked+" from "+self.chan+" : "+self.raison,"#888888","#888888",True))
                    self.get_list(self.chan)

            if(self.message_id == 'QUIT'):
                self.sender = self.getNick(self.line[0])
                self.i = 0
                message = " has quit"
                while(self.i < len(self.chans)):
                    if(self.sender.lower() in self.filtrer_liste(self.names[self.i])):
                        self.messages[self.i].append(self.html_convert(self.sender,message,"#888888","#888888",True))
                        self.get_list(self.chans[self.i])
                    self.i += 1

            if(self.message_id == 'PRIVMSG' or self.message_id == 'NOTICE' and len(self.line) > 2):
                self.sender = self.getNick(self.line[0])
                if(self.line[2][0] == "#"):
                    self.window = self.line[2].lower()
                    if(self.Nick.lower() not in self.getMsg(self.line)):
                        self.generated_color = str(self.GenColor(self.sender)).replace("0x","")
                        self.color = "#"+self.generated_color[0]+self.generated_color[0]+self.generated_color[1]+self.generated_color[1]+self.generated_color[2]+self.generated_color[2]# Pseudo normal

                        self.message_color = "#000000"
                    else :
                        self.color = "#EE00EE"
                        self.message_color = "#EE00EE"
                        self.playsound()

                else:
                    if(self.sender.lower() != "playonlinux"):
                        self.color = "#AA0000"
                        self.message_color = "#000000"
                        self.window = self.sender.lower()
                        if(self.window != self.selected_window and not "." in self.window):
                            self.playsound()
                        self.old_window = self.selected_window
                        if(self.window not in self.chans):
                            self.chans.append(self.window)
                            self.endnames.append(False)
                            self.names.append([])
                            self.messages.append([])
                        if(self.old_window != ""):
                            self.select_window = self.old_window

                self.index = self.get_index(self.window)
                if("\x01ACTION" in self.getMsg(self.line)):
                    message = self.getMsg(self.line).replace("\x01","")
                    message = message[6:len(message)]
                    if(self.sender.lower() != "playonlinux"):
                        self.messages[self.index].append(self.html_convert(self.sender,message,"#000088","#000088",True))
                else :
                    message = self.getMsg(self.line)
                    if(self.sender.lower() != "playonlinux"):
                        self.messages[self.index].append(self.html_convert(self.sender,message,self.color,self.message_color))
                    else:
                        message_split = message.split(" ")
                        if(len(message_split) >= 2):
                            if(message_split[0] == "ALLOW"):
                                allowed_people.append(message_split[1])
                            elif(message_split[0] == "DENY"):
                                refused_people.append(message_split[1])

            #print self.names
    def run(self):
        self.ircconnected = False
        self.selected_window = self.chanAutoJoin
        self.names = []
        self.messages = []
        self.chans = []
        self.endnames = []
        self.select_window = ""
        self.status_messages = []
       # self.open_window = []
        while 1:
            if(self.ircconnected == True):
                #select([self.connexion], [], [])
                self.dataRecv = self.connexion.recv(1024)
                self.contentParse_ = string.split(self.dataRecv,"\r\n")
                self.k = 0
                while(self.k < len(self.contentParse_)):
                    if(self.contentParse_[self.k]):
                        self.traiter(self.contentParse_[self.k])
                    self.k += 1
            else:
                time.sleep(0.1)

    def Connexion(self):
        self.connect()

    def stop(self):
        if(self.ircconnected == True):
               # self.zone_append("<font color='#666666'>("+time.strftime("%H:%M:%S")+") Disconnected</font>")
            self.ircconnected = False
            self.status_messages.append(self.html_convert(None, "Disconnected","#AA0000","#AA0000",True))
            self.connexion.send("QUIT :www.playonlinux.com\r\n")
            self.connexion.close()
            self.names = []
            self.messages = []
            self.chans = []
            self.endnames = []
