#!/usr/bin/env python3

#
# The Qubes OS Project, https://www.qubes-os.org/
#
# Copyright (C) 2018  Wojtek Porczyk <woju@invisiblethingslab.com>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

QREXEC_CLIENT = '/usr/bin/qrexec-client-vm'

import subprocess
import sys

def _qrexec(rpcname, *, name=None, argument=None, input=None):
    if name is not None:
        rpcname = '{}+{}'.format(rpcname, name)

    kwds = {}
    if argument is None and input is None:
        kwds['stdin'] = subprocess.DEVNULL
    else:
        if argument is None:
            argument = b'\xff'
        else:
            if not isinstance(argument, bytes):
                argument = argument.encode()
            argument = bytes((len(argument),)) + argument

        if input is None:
            input = b''
        elif not isinstance(input, bytes):
            input = input.encode()

        kwds['input'] = argument + input

    return subprocess.check_output(
        [QREXEC_CLIENT, 'dom0', rpcname], **kwds).decode()

class policy:
    @staticmethod
    def List(name=None):
        return _qrexec('policy.List', name=name).rstrip('\n').split('\n')

    @staticmethod
    def Get(name, *, argument=None):
        return _qrexec('policy.Get', name=name, argument=argument)

    @staticmethod
    def Replace(name, input, *, argument=None):
        return _qrexec('policy.Replace', name=name, argument=argument,
            input=input)

    @staticmethod
    def Remove(name, *, argument=None):
        return _qrexec('policy.Remove', name=name, argument=argument)

    class include:
        @staticmethod
        def List():
            return _qrexec('policy.include.List',
                ).rstrip('\n').split('\n')

        @staticmethod
        def Get(name):
            return _qrexec('policy.include.Get', name=name)

        @staticmethod
        def Replace(name, input):
            return _qrexec('policy.Replace', name=name, input=input)

        @staticmethod
        def Remove(name):
            return _qrexec('policy.Remove', name=name)
