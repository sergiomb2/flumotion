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

from twisted.internet import defer

from flumotion.common import messages
from flumotion.common.i18n import N_, gettexter

__version__ = "$Rev$"
T_ = gettexter()


def get_gst_version(gst):
    if hasattr(gst, 'get_gst_version'):
        return gst.get_gst_version()
    elif hasattr(gst, 'version'):
        return gst.version()
    else:
        return gst.gst_version + (0, )


def get_pygst_version(gst):
    if hasattr(gst, 'get_pygst_version'):
        return gst.get_pygst_version()
    else:
        return gst.pygst_version + (0, )


def checkTicket347():
    """
    Check for a recent enough PyGTK to not leak python integers in message
    processing (mostly affects soundcard, firewire)
    """
    result = messages.Result()
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import GObject

    result.succeed(None)
    return defer.succeed(result)


def checkTicket348():
    result = messages.Result()
    from gi.repository import Gst

    result.succeed(None)
    return defer.succeed(result)


def checkTicket349():
    result = messages.Result()
    import pygst
    pygst.require('0.10')
    import gst

    if get_gst_version(gst) < (0, 10, 4, 1):
        major, minor, micro, nano = get_gst_version(gst)
        m = messages.Error(T_(
            N_("Version %d.%d.%d of the GStreamer library is too old.\n"),
            major, minor, micro),
            mid='ticket-349')
        m.add(T_(N_("The '%s' component needs a newer version of '%s'.\n"),
                    'looper', 'gstreamer'))
        m.add(T_(N_("Please upgrade '%s' to version %s or later."),
            'gstreamer', '0.10.5'))
        result.add(m)

    if get_pygst_version(gst) < (0, 10, 3, 1):
        major, minor, micro, nano = get_pygst_version(gst)
        m = messages.Error(T_(
            N_("Version %d.%d.%d of the gst-python library is too old.\n"),
            major, minor, micro),
            mid='ticket-349')
        m.add(T_(N_("The '%s' component needs a newer version of '%s'.\n"),
                    'looper', 'gst-python'))
        m.add(T_(N_("Please upgrade '%s' to version %s or later."),
            'gst-python', '0.10.4'))
        result.add(m)

    result.succeed(None)
    return defer.succeed(result)
