#
# UrT Fenix Manager Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2013 Daniele Pantaleone <fenix@bigbrotherbot.net>
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# CHANGELOG:
#
# 07/02/2014 - 1.0 - Fenix
#   * initial version
# 09/02/2014 - 1.1 - Fenix
#   * register events using the event id
#

__author__ = 'Fenix'
__version__ = '1.1'

import b3
import b3.plugin
import b3.events

from ConfigParser import NoOptionError


class UrtfenixPlugin(b3.plugin.Plugin):

    _adminPlugin = None

    _settings = dict(cmd_color_code=5)

    ####################################################################################################################
    ##                                                                                                                ##
    ##   STARTUP                                                                                                      ##
    ##                                                                                                                ##
    ####################################################################################################################

    def __init__(self, console, config=None):
        """
        Build the plugin object
        """
        b3.plugin.Plugin.__init__(self, console, config)
        if self.console.gameName != 'iourt42':
            self.critical("unsupported game : %s" % self.console.gameName)
            raise SystemExit(220)

        # check for correct server engine version
        version = self.console.getCvar('version').getString()
        if not version.startswith('ioQ3 1.35 urt-fenix'):
            self.critical("unsupported server engine : %s" % version)
            raise SystemExit(220)

        # get the admin plugin
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.critical('could not start without admin plugin')
            raise SystemExit(220)

    def onLoadConfig(self):
        """\
        Load plugin configuration
        """
        try:
            if self.config.getint('settings', 'cmd_color_code') not in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
                raise ValueError('color code out of range [0-9]')
            self._settings['cmd_color_code'] = self.config.getint('settings', 'cmd_color_code')
            self.debug('loaded settings/cmd_color_code setting: %s' % self._settings['cmd_color_code'])
        except NoOptionError:
            self.warning('could not find settings/cmd_color_code in config file, '
                         'using default: %s' % self._settings['cmd_color_code'])
        except ValueError, e:
            self.error('could not load settings/cmd_color_code config value: %s' % e)
            self.debug('using default value (%s) for settings/cmd_color_code' % self._settings['cmd_color_code'])

    def onStartup(self):
        """\
        Initialize plugin settings
        """
        # register our commands
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

        # register the events needed
        self.registerEvent(self.console.getEventID('EVT_CLIENT_SAY'), self.onSay)

        # notice plugin startup
        self.debug('plugin started')

    ####################################################################################################################
    ##                                                                                                                ##
    ##   FUNCTIONS                                                                                                    ##
    ##                                                                                                                ##
    ####################################################################################################################

    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func
        return None

    ####################################################################################################################
    ##                                                                                                                ##
    ##   EVENTS                                                                                                       ##
    ##                                                                                                                ##
    ####################################################################################################################

    def onSay(self, event):
        """\
        Handle EVT_CLIENT_SAY
        """
        if event.data[0] in (self._adminPlugin.cmdPrefix, self._adminPlugin.cmdPrefixLoud,
                             self._adminPlugin.cmdPrefixBig, self._adminPlugin.cmdPrefixPrivate):

            # command abuse check: if the client who issued a b3 command is
            # admin on this server, forward the command he just issued to all
            # the other connected clients who are in a equal/higher group
            if event.client.maxLevel >= self._adminPlugin._admins_level:

                client = event.client
                for admin in self._adminPlugin.getAdmins():
                    if admin != client and admin.maxLevel >= client.maxLevel:
                        admin.message('^7%s: ^%s%s' % (client.name, self._settings['cmd_color_code'], event.data))

    ####################################################################################################################
    ##                                                                                                                ##
    ##   COMMANDS                                                                                                     ##
    ##                                                                                                                ##
    ####################################################################################################################

    def cmd_pm(self, data, client, cmd=None):
        """\
        <client> <message> - send a private message to a client
        """
        m = self._adminPlugin.parseUserCmd(data)
        if not m or not m[0] or not m[1]:
            client.message('^7invalid data, try ^3!^7help pm')
            return

        cid, msg = m
        sclient = self._adminPlugin.findClientPrompt(cid, client)
        if not sclient:
            return

        # send the private message
        sclient.message('^7%s: ^3%s' % (client.name, msg))

    def cmd_radio(self, data, client, cmd=None):
        """\
        Set the use of the radio <on/off>
        """
        if not data or data not in ('on', 'off'):
            client.message('^7invalid data, try ^3!^7help radio')
            return

        if data == 'on':
            self.console.setCvar('sv_disableradio', '0')
            self.console.say('^7Radio: ^2ON')
        elif data == 'off':
            self.console.setCvar('sv_disableradio', '1')
            self.console.say('^7Radio: ^1OFF')

    def cmd_teleport(self, data, client, cmd=None):
        """\
        <client> - teleport to a specific client
        """
        if not data:
            client.message('^7missing data, try ^3!^7help teleport')
            return

        sclient = self._adminPlugin.findClientPrompt(data, client)
        if not sclient:
            return

        # send the teleport command
        self.console.write('teleport %s %s' % (client.cid, sclient.cid))
