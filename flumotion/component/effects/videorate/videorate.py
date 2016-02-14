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

from gi.repository import GObject
from gi.repository import Gst

from flumotion.component import feedcomponent
from flumotion.common import gstreamer

__version__ = "$Rev$"


class VideorateBin(Gst.Bin):
    """
    I am a GStreamer bin that can change the framerate of a video stream.
    """
    logCategory = "videosrate"
    CAPS_TEMPLATE = "video/x-raw%(fr)s;"\
                    "video/x-raw%(fr)s"

    __gproperties__ = {
        'framerate': (GObject.TYPE_OBJECT, 'framerate',
                   'Video framerate', GObject.PARAM_READWRITE)}

    def __init__(self, framerate=Gst.Fraction(25, 1)):
        Gst.Bin.__init__(self)
        self._framerate = framerate

        self._videorate = Gst.ElementFactory.make("videorate")
        self._capsfilter = Gst.ElementFactory.make("capsfilter")
        self.add(self._videorate, self._capsfilter)

        self._videorate.link(self._capsfilter)

        # Set properties
        if gstreamer.element_has_property(self._videorate, 'skip-to-first'):
            self._videorate.set_property('skip-to-first', True)

        # Create source and sink pads
        self._sinkPad = Gst.GhostPad.new('sink', self._videorate.get_static_pad('sink'))
        self._srcPad = Gst.GhostPad.new('src', self._capsfilter.get_static_pad('src'))
        self.add_pad(self._sinkPad)
        self.add_pad(self._srcPad)

        self._setFramerate(framerate)

    def _setFramerate(self, framerate):
        self._framerate = framerate
        self._capsfilter.set_property('caps',
            Gst.Caps(self.CAPS_TEMPLATE % dict(fr=self.framerateToString())))

    def do_set_property(self, property, value):
        if property.name == 'framerate':
            self._setFramerate(value)
        else:
            raise AttributeError('unknown property %s' % property.name)

    def do_get_property(self, property):
        if property.name == 'framerate':
            return self._framerate
        else:
            raise AttributeError('unknown property %s' % property.name)

    def framerateToString(self):
        if self._framerate is None:
            return ""
        return ",framerate=(fraction)%d/%d" % (self._framerate.num,
            self._framerate.denom)


class Videorate(feedcomponent.PostProcEffect):
    """
    I am an effect that can be added to any component that has a videorate
    component and a way of changing the output framerate.
    """
    logCategory = "videorate-effect"

    def __init__(self, name, sourcePad, pipeline, framerate):
        """
        @param element:     the video source element on which the post
                            processing effect will be added
        @param sourcePad:   source pad used for linking the effect
        @param pipeline:    the pipeline of the element
        @param framerate:   output framerate
        """
        feedcomponent.PostProcEffect.__init__(self, name, sourcePad,
            VideorateBin(framerate), pipeline)

    def effect_setFramerate(self, framerate):
        self.effectBin.set_property("framerate", framerate)
        return framerate

    def effect_getFramerate(self):
        return self.effectBin.get_property('framerate')
