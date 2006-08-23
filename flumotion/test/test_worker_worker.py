# -*- Mode: Python; test-case-name:flumotion.test.test_worker_worker -*-
# vi:si:et:sw=4:sts=4:ts=4
#
# Flumotion - a streaming media server
# Copyright (C) 2004,2005,2006 Fluendo, S.L. (www.fluendo.com).
# All rights reserved.

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE.GPL" in the source distribution for more information.

# Licensees having purchased or holding a valid Flumotion Advanced
# Streaming Server license may use this file in accordance with the
# Flumotion Advanced Streaming Server Commercial License Agreement.
# See "LICENSE.Flumotion" in the source distribution for more information.

# Headers in this file shall remain intact.

import common
from twisted.trial import unittest

from twisted.internet import reactor, defer

from flumotion.worker import worker

import twisted.copyright #T1.3
#T1.3
def weHaveAnOldTwisted():
    return twisted.copyright.version[0] < '2'

class TestKid(unittest.TestCase):
    def testGetPid(self):
        kid = worker.Kid(1092, "kid", "http", "module", "method", 5,
            [('belgian', '/opt/ion/al'), ('american', '/ess/en/tial')])
        self.assertEquals(kid.avatarId, "kid")
        self.assertEquals(kid.type, "http")
        self.assertEquals(kid.nice, 5)
        self.assertEquals(len(kid.bundles), 2)

        self.assertEquals(kid.pid, 1092)

class TestKindergarten(unittest.TestCase):
    def testInit(self):
        kg = worker.Kindergarten({}, "", {})
        self.assertEquals(kg.options, {})
        self.assertEquals(kg._kids, {})

    def testRemoveKidByPid(self):
        kg = worker.Kindergarten({}, "", {})
        kg._kids['/swede/johan'] = worker.Kid(1, "/swede/johan", "http",
            "module", "method", {}, [('foo', 'bar')])

        self.assertEquals(kg.removeKidByPid(2), False)

        self.assertEquals(kg.removeKidByPid(1), True)
        self.assertEquals(kg._kids, {})

class FakeOptions:
    def __init__(self):
        self.host = 'localhost'
        self.port = 9999
        self.transport = 'TCP'
        self.feederports = [9998]
        self.name = 'fakeworker'
    
class TestWorkerClientFactory(unittest.TestCase):
    def testInit(self):
        brain = worker.WorkerBrain(FakeOptions())
        factory = worker.WorkerClientFactory(brain)

        d = brain.teardown()
        if weHaveAnOldTwisted():
            unittest.deferredResult(d)
        else:
            return d

class FakeRef:
    def __init__(self):
        self._callbacks = []

    def notifyOnDisconnect(self, callback):
        self._callbacks.append(callback)

    def callRemote(self, method, *args, **kwargs):
        return defer.succeed(None)

    def _disconnect(self):
        for cb in self._callbacks:
            cb(self)

class TestWorkerMedium(unittest.TestCase):
    def testSetRemoteReference(self):
        brain = worker.WorkerBrain(FakeOptions())
        self.medium = worker.WorkerMedium(brain, [])
        ref = FakeRef()
        self.medium.setRemoteReference(ref)
        self.assert_(self.medium.hasRemoteReference())

        ref._disconnect()

        d = brain.teardown()
        if weHaveAnOldTwisted():
            unittest.deferredResult(d)
        else:
            return d

# FIXME: add tests to test signal handler ? Might not be so easy.
