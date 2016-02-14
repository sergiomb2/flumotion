# -*- Mode: Python; test-case-name: flumotion.test.test_feedcomponent010 -*-
# vi:si:et:sw=4:sts=4:ts=4

# Flumotion - a streaming media server
# Copyright (C) 2004,2005,2006,2007,2008,2009 Fluendo, S.L.
# Copyright (C) 2010,2011 Flumotion Services, S.A.
# All rights reserved.
#
# This file may be distributed and/or modified under the terms of
# the GNU Lesser General Public License version 2.1 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE.LGPL" in the source distribution for more information.
#
# Headers in this file shall remain intact.

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from twisted.internet import defer, reactor
from twisted.trial import unittest

from flumotion.common import testsuite
from flumotion.component import padmonitor

attr = testsuite.attr


class TestPadMonitor(testsuite.TestCase):

    slow = True

    def _run_pipeline(self, pipeline):
        pipeline.set_state(Gst.State.PLAYING)
        pipeline.get_bus().poll(Gst.MessageType.EOS, 18446744073709551615L)#Gst.CLOCK_TIME_NONE
        pipeline.set_state(Gst.State.NULL)

    def testPadMonitorActivation(self):
        pipeline = Gst.parse_launch(
            'fakesrc num-buffers=1 ! identity name=id ! fakesink')
        identity = pipeline.get_by_name('id')

        srcpad = identity.get_static_pad('src')
        monitor = padmonitor.PadMonitor(srcpad, "identity-source",
                                        lambda name: None,
                                        lambda name: None)
        self.assertEquals(monitor.isActive(), False)

        self._run_pipeline(pipeline)
        # Now give the reactor a chance to process the callFromThread()
        d = defer.Deferred()

        def finishTest():
            self.assertEquals(monitor.isActive(), True)
            monitor.detach()
            d.callback(True)
        reactor.callLater(0.1, finishTest)

        return d

    def testPadMonitorTimeout(self):
        padmonitor.PadMonitor.PAD_MONITOR_PROBE_INTERVAL = 0.2
        padmonitor.PadMonitor.PAD_MONITOR_CHECK_INTERVAL = 0.5

        pipeline = Gst.parse_launch(
            'fakesrc num-buffers=1 ! identity name=id ! fakesink')
        identity = pipeline.get_by_name('id')

        srcpad = identity.get_static_pad('src')

        # Now give the reactor a chance to process the callFromThread()

        def finished():
            monitor.detach()
            d.callback(True)

        def hasInactivated(name):
            # We can't detach the monitor from this callback safely, so do
            # it from a reactor.callLater()
            reactor.callLater(0, finished)

        def hasActivated():
            self.assertEquals(monitor.isActive(), True)
            # Now, we don't send any more data, and after our 0.5 second
            # timeout we should go inactive. Pass our test if that happens.
            # Otherwise trial will time out.

        monitor = padmonitor.PadMonitor(srcpad, "identity-source",
                                        lambda name: None,
                                        hasInactivated)
        self.assertEquals(monitor.isActive(), False)

        self._run_pipeline(pipeline)

        d = defer.Deferred()

        reactor.callLater(0.2, hasActivated)

        return d

if __name__ == '__main__':
    unittest.main()
