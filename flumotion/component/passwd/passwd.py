# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Flumotion - a video streamer server
# Copyright (C) 2004 Fluendo
#
# flumotion/component/passwd/passwd.py: implements .htpasswd authentication
#
# Flumotion - a streaming media server
# Copyright (C) 2004 Fluendo (www.fluendo.com)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# See "LICENSE.GPL" in the source distribution for more information.

# This program is also licensed under the Flumotion license.
# See "LICENSE.Flumotion" in the source distribution for more information.

import crypt

from twisted.python import components
from flumotion.common import interfaces
from flumotion.component import component

__all__ = ['HTTPGatekeeper']

# FIXME: needs to be renamed to a bouncer type
class HTTPGatekeeper:

    __implements__ = interfaces.IAuthenticate,
    
    def __init__(self, filename, type):
        self.filename = filename
        self.type = type

        self.db = {}
        for line in open(filename).readlines() :
            name, passwd = line[:-1].split(':')
            self.db[name] = passwd

        self.domain = 'default'
        
    def setDomain(self, name):
        self.domain = name

    def getDomain(self):
        return self.domain
    
    def authenticate(self, keycard):
        if not components.implements(keycard, interfaces.IClientKeycard):
            raise AssertionError

        username = keycard.getUsername()
        if not self.db.has_key(username):
            return False

        entry = self.db[username]
        if self.type == 'crypt':
            salt = entry[:2]
            encrypted = crypt.crypt(keycard.getPassword(), salt)
        elif self.type == 'md5':
            raise NotImplementedError
        else:
            raise AssertionError("unsupported method: %s" % self.type)

        return entry == encrypted

def createComponent(config):
    filename = config['filename']
    type = config.get('auth-type', 'crypt')
    
    return HTTPGatekeeper(filename, type)
