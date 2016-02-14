# -*- Mode: Python; test-case-name: flumotion.test.test_common_gstreamer -*-
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
from twisted.trial import unittest
from flumotion.common import gstreamer

Gst.init(None)

class Factory(unittest.TestCase):

    def testFakeSrc(self):
        hassync = gstreamer.element_factory_has_property('fakesrc', 'sync')
        self.failUnless(hassync)
        hasync = gstreamer.element_factory_has_property('fakesrc', 'ync')
        self.failIf(hasync)


class Caps(unittest.TestCase):

    def testCaps(self):
        caps = Gst.caps_from_string(
            'video/x-raw,width=10,framerate=5.0;video/x-raw,'
            'width=15,framerate=10.0')
        self.assertEquals(gstreamer.caps_repr(caps),
            'video/x-raw, width=(int)10, '
                          'framerate=(double)5; video/x-raw, '
                          'width=(int)15, framerate=(double)10')

    def testCapsStreamheader(self):
        caps = Gst.caps_from_string('application/ogg,streamheader=abcd')
        self.assertEquals(gstreamer.caps_repr(caps),
            'streamheader=<...>')


class FakeComponent:

    def debug(self, string):
        pass


def run_it_a_little_while(p):
    p.set_state(Gst.State.PLAYING)
    m = p.get_bus().poll(Gst.MESSAGE_EOS, -1)
    p.set_state(Gst.State.NULL)


class DeepNotify(unittest.TestCase):

    def testDeepNotify(self):
        component = FakeComponent()
        pipeline = Gst.parse_launch('fakesrc num-buffers=3 ! fakesink')
        pipeline.connect('deep-notify', gstreamer.verbose_deep_notify_cb,
            component)


class TestProperty(unittest.TestCase):

    def testHasProperty(self):
        b = gstreamer.element_factory_has_property('fakesrc', 'num-buffers')
        self.failUnless(b)
        b = gstreamer.element_factory_has_property('fakesrc', 'i-do-not-exist')
        self.failIf(b)

    def testHasPropertyValue(self):
        b = gstreamer.element_factory_has_property_value(
            'fakesrc', 'num-buffers', 1)
        self.failUnless(b)
        # setting string values for enums only works in 0.10, or something
        b = gstreamer.element_factory_has_property_value(
            'fakesrc', 'sizetype', 'fixed')
        self.failUnless(b)
        b = gstreamer.element_factory_has_property_value(
            'fakesrc', 'sizetype', 'no-way')
        self.failIf(b)
