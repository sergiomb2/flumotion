# -*- Mode: Python; test-case-name: flumotion.test.test_common_pygobject -*-
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

from gi.repository import GObject
from gi.repository import Gtk

from flumotion.common import testsuite
from flumotion.common import errors, pygobject
from flumotion.common.pygobject import gsignal, gproperty


class SetProperty(testsuite.TestCase):

    def testButton(self):
        b = Gtk.Button()

        # string
        pygobject.gobject_set_property(b, 'name', 'button')
        self.assertRaises(errors.PropertyError,
            pygobject.gobject_set_property, b, 'doesnotexist', 'somevalue')

        # int
        pygobject.gobject_set_property(b, 'width-request', 1)
        self.assertRaises(errors.PropertyError,
            pygobject.gobject_set_property, b, 'width-request', 'notanint')

        # boolean
        pygobject.gobject_set_property(b, 'can-focus', 'True')
        self.assertEquals(b.get_property('can-focus'), True)
        pygobject.gobject_set_property(b, 'can-focus', 'False')
        self.assertEquals(b.get_property('can-focus'), False)
        pygobject.gobject_set_property(b, 'can-focus', 'something')
        self.assertEquals(b.get_property('can-focus'), True)
        pygobject.gobject_set_property(b, 'can-focus', [])
        self.assertEquals(b.get_property('can-focus'), False)


class TestPyGObject(testsuite.TestCase):

    def testPyGObject(self):

        class Foo(GObject.GObject):
            gsignal('hcf', bool, str)
            gproperty(bool, 'burning', 'If the object is burning',
                      False)

            def __init__(xself):
                GObject.GObject.__init__(xself)
                xself.connect('hcf', xself.on_hcf)
                xself.set_property('burning', False)

            def on_hcf(xself, again_self, x, y):
                self.assert_(isinstance(x, bool))
                self.assert_(isinstance(y, str))
                xself.set_property('burning', True)
        GObject.type_register(Foo)

        o = Foo()

        self.assertEquals(False, o.get_property('burning'))
        o.emit('hcf', False, 'foogoober')
        self.assertEquals(True, o.get_property('burning'))
