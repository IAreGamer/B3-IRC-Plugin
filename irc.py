#
# IRC Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2012 ShootingBlanks
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# self.console.cron + b3.cron.OneTimeCronTab(self.update_vote,  "*/%s" %self._vote_interval_announcements)
# self._cronTab = b3.cron.PluginCronTab(self, self.croncheck, '*/%s' % (30))

     #   client.setvar(self, self._clientvar_name, SpreeStats())
     #   if not client.isvar(self, self._clientvar_name):
     #   client.setvar(self, self._clientvar_name, SpreeStats())
          
     #         return client.var(self, self._clientvar_name).value
     #      spreeStats = self.get_spree_stats(client)
     #       spreeStats.kills += 1

__version__ = '1.0'
__author__  = 'Shootingblanks'

import b3, thread, time
import b3.events
import b3.plugin
import b3.cron
import socket
import string

    
class IrcPlugin(b3.plugin.Plugin):
    host="irc.q3ut4.com"
    port=6667
    nick="b3bot"
    realName = "B3 IRC BOT"
    group_channel = ""
    all_channel = ""
    cmd_level = 1
    net_ip = None
    net_port = None
    hostname =""
    gamelist = ['FFA','','','TDM','TS','CaH','FTL','CTF','Bomb']
    gametype = None 
    playercount = 0
    _clientvar = 'socket'
    sock = None
    nicktranslate = None
          
    def onLoadConfig(self):
         self.cmd_level = self.config.getint('settings', 'cmd_level') 
         self.host = self.config.get('settings', 'host') 
         self.port = self.config.getint('settings', 'port') 
         self.nick = self.config.get('settings', 'nick') 
         self.my_channel = self.config.get('settings', 'my_channel') 
         self.group_channel = self.config.get('settings', 'group_channel') 
         self.all_channel = self.config.get('settings', 'all_channel') 
         
         
    def onStartup(self):
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
             # something is wrong, can't start without admin plugin
             self.error('Could not find admin plugin')
             return
        
        
        self._adminPlugin.registerCommand(self, 'irc', self.cmd_level, self.cmd_irc)
        self.registerEvent(b3.events.EVT_GAME_MAP_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_CLIENT_CONNECT)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.net_ip = self.console.getCvar('net_ip').getString()
        self.net_port = self.console.getCvar('net_port').getString()
        self.hostname = self.console.getCvar('sv_hostname').getString()
        self.sock=socket.socket( )
        self.sock.connect((self.host, self.port))
        self.sock.send("nick %s\r\n" % self.nick)
        self.sock.send("USER %s %s bla :/connect %s %s\r\n" % (self.nick, self.nick, self.net_ip, self.net_port))
        self.sock.send("JOIN %s \r\n" % (self.all_channel))
        self.sock.send('JOIN %s \r\n' % (self.group_channel))  
        self.sock.send("JOIN %s \r\n" % (self.my_channel))
        
        thread.start_new_thread(self.irc_read, ())

           
    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if event.type == b3.events.EVT_CLIENT_CONNECT:
           tclient = event.client
           #self.sock.send("PRIVMSG %s :%s Connected \r\n" % (self.group_channel,tclient.name)) 


        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            tclient = event.client
            #self.sock.send("PRIVMSG %s :%s Disconnected\r\n" % (self.group_channel, tclient.name)) 
            
        elif event.type == b3.events.EVT_GAME_MAP_CHANGE:
            
            #get players, map, gametype. Announce on #all
            self.gametype = self.console.getCvar('g_gametype').getInt()
            map = self.console.getCvar('mapname').getString()
            self.sock.send("PRIVMSG %s :%s %s %s players /connect %s.%s\r\n" % (self.gamelist[self.gametype], map, self.playerCount, self.group_channel,self.net_ip,self.net_port,)) 
        elif event.type == b3.events.EVT_GAME_EXIT:
            self.playerCount = len(self.console.clients.getList())
            #self.sock.send("PRIVMSG  %s :/connect %s:%s %s on %s, %s players\r\n" % (self.group_channel,self.net_ip,self.net_port,self.gamelist[gametype],map,self.playerCount)) 

   
            
    def irc_read(self):
        #msg is broken up into parts
        # 0  prefix includes sent from
        # 1 is the message type (JOIN PRIVMSG ETC)
        # 2 is the channel
        # 3 is the : and the message
        while True:
            readbuffer = self.sock.recv(4096)
            msg = string.split(readbuffer,None,3)
            if readbuffer == "":
                self.sock.send('QUIT')
                self.sock.close()

            elif readbuffer.find('PING') != -1: #If PING is Found in the Data
               self.sock.send('PONG ' + readbuffer.split()[1] + '\r\n') #Send back a PONG 

            elif msg[1] == 'PRIVMSG':
               sentfrom = string.split(msg[0],'!',1)
               #parse_privmsg(readbuffer)
               self.console.say('^3%s %s' %(sentfrom[0],msg[3]))
               #:ShootingBlanks!"ShootingB@69.60.120.27 :test
                          
    def parse_privmsg(data):
        msg = data.split()
        
        
    def cmd_irc(self, data, client, cmd):
            """\
            <channel> <message>- Send an IRC message.
            Channel is optional and can be a channel or #all
            """
           
            if len(data) != 0:
                message = string.split(data,None,1)
                channel = message[0]
                #msg 0 is either command or recipient
                #msg 1 is message. 
                #if msg 0 == a command we have to send entire message because it will contain arguments
                # create a dictionary of commands and match those to msg[0]
                #if msg[0]find('') != -1: #send to specific channel
                #send_socket.send("PRIVMSG  #%s :<%s> %s \r\n" % (self.all_channel, client.name, msg[1]))     
                #send to person or channel
                if channel[0] =='#': 
                    #its to a specific channel
                    self.sock.send("PRIVMSG %s :%s->%s \r\n" % (message[0], client.name, message[1])) 
                   
                else:
                    self.sock.send("PRIVMSG %s :%s->%s \r\n" % (self.all_channel, client.name, data)) 
                    
                
                
                #else: #send to my group channel
                #    send_socket.send("#%s :<%s> %s \r\n" % (self.group_channel, client.name, data)) 
            else:
            #no data
                client.message("You didn't say anything")           
