# -*- Mode: Python -*-
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

import os

import flumotion.common.setup
# logging
flumotion.common.setup.setup()

from flumotion.common import log


def useGtk3Reactor():
    var = 'FLU_TEST_GTK3_REACTOR'

    if var not in os.environ:
        return False
    else:
        return True

if useGtk3Reactor():
    log.info('check', 'using gtk3 reactor')
    from twisted.internet import gtk3reactor
    gtk3reactor.install()
else:
    log.info('check', 'using default reactor')

# have to choose the reactor before calling this method
log.logTwisted()

# FIXME: boot.py does this, but enabling this borks
# test_common_package.py. I have no idea what that code does, either.
#
# # installing the reactor could override our packager's import hooks ...
# from twisted.internet import reactor
# # ... so we install them again here to be safe
# from flumotion.common import package
# package.getPackager().install()

# make sure we have the right gst-python version
from flumotion.common import boot
boot.init_gobject()
boot.init_gst()

# fdpass is a built module,  so it lives in builddir, while the package
# __init__ is in srcdir.  Append to its __path__ to make the tests work
i = os.getcwd().find('_build')
if i > -1:
    top_builddir = os.path.join(os.getcwd()[:i], '_build')
    from flumotion.extern import fdpass
    fdpass.__path__.append(os.path.join(top_builddir, 'flumotion', 'extern',
        'fdpass'))

del boot, flumotion, i, log, useGtk3Reactor
