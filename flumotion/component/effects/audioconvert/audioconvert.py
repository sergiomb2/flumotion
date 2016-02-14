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

import sys

from gi.repository import GObject
from gi.repository import Gst

from flumotion.common.i18n import gettexter
from flumotion.component import feedcomponent
from flumotion.common import gstreamer

__version__ = "$Rev$"
T_ = gettexter()

DEFAULT_TOLERANCE = 20000000 # 20ms


class AudioconvertBin(Gst.Bin):
    """
    I am a GStreamer bin that can convert an an audio stream, changing its
    samplerate and the number of channels
    """
    logCategory = "audiorate"
    RATE_CAPS = ', rate=%d'
    CHANNELS_CAPS = ', channels=%d'
    CAPS_TEMPLATE = ("audio/x-raw %(extra_caps)s ;"
                    "audio/x-raw %(extra_caps)s")

    __gproperties__ = {
        'channels': (GObject.TYPE_UINT, 'channels',
                       'Audio channels', 1, 8, 2,
                       GObject.PARAM_READWRITE),
        'samplerate': (GObject.TYPE_UINT, 'samplerate',
                       'Audio samplerate', 1, 200000, 44100,
                       GObject.PARAM_READWRITE),
        'tolerance': (GObject.TYPE_UINT, 'tolerance',
                       'Correct imperfect timestamps when it exeeds the '
                       'tolerance', 0, sys.maxint, DEFAULT_TOLERANCE,
                       GObject.PARAM_READWRITE)}

    def __init__(self, channels=None, samplerate=None,
                 tolerance=DEFAULT_TOLERANCE):
        Gst.Bin.__init__(self)
        self._samplerate = samplerate
        self._samplerate_caps = ''
        self._channels = channels
        self._channels_caps = ''

        if self._use_audiorate():
            self._audiorate = Gst.ElementFactory.make("audiorate")
            self._audiorate.set_property("skip-to-first", True)
        else:
            self._audiorate = Gst.ElementFactory.make("identity")
            self._audiorate.set_property("silent", True)

        self._audioconv = Gst.ElementFactory.make("audioconvert")

        resampler = 'audioresample'
        if gstreamer.element_factory_exists('legacyresample'):
            resampler = 'legacyresample'
        self._audioresample = Gst.ElementFactory.make(resampler)

        self._capsfilter = Gst.ElementFactory.make("capsfilter")
        self._identity = Gst.parse_launch("identity silent=true")
        self.add(self._audiorate)
        self.add(self._audioconv)
        self.add(self._audioresample)
        self.add(self._capsfilter)
        self.add(self._identity)

        self._audiorate.link(self._audioconv)
        self._audioconv.link(self._audioresample)
        self._audioresample.link(self._capsfilter)
        self._capsfilter.link(self._identity)

        # Create source and sink pads
        self._sinkPad = Gst.GhostPad.new('sink', self._audiorate.get_static_pad('sink'))
        self._srcPad = Gst.GhostPad.new('src', self._identity.get_static_pad('src'))
        self.add_pad(self._sinkPad)
        self.add_pad(self._srcPad)

        self._setSamplerate(samplerate)
        self._setChannels(channels)
        self._setTolerance(tolerance)

    def _use_audiorate(self):
        return gstreamer.element_factory_has_property('audiorate',
                                                      'skip-to-first')

    def _getCapsString(self):
        extra_caps = ' '.join([self._samplerate_caps, self._channels_caps])
        return self.CAPS_TEMPLATE % dict(extra_caps=extra_caps)

    def _setChannels(self, channels):
        self._channels = channels
        self._channels_caps = ''
        if self._channels is not None:
            self._channels_caps = self.CHANNELS_CAPS % channels
        self._capsfilter.set_property('caps', Gst.Caps(self._getCapsString()))

    def _setSamplerate(self, samplerate):
        self._samplerate = samplerate
        self._samplerate_caps = ''
        if self._samplerate is not None:
            self._samplerate_caps = self.RATE_CAPS % samplerate
        self._capsfilter.set_property('caps', Gst.Caps(self._getCapsString()))

    def _setTolerance(self, tolerance):
        self._tolerance = tolerance
        if gstreamer.element_has_property(self._audiorate, 'tolerance'):
            self._audiorate.set_property('tolerance', self._tolerance)
        else:
            self.warning("The 'tolerance' property could not be set in the "
                         "audiorate element.")

    def do_set_property(self, property, value):
        if property.name == 'channels':
            self._setChannels(value)
        if property.name == 'samplerate':
            self._setSamplerate(value)
        if property.name == 'tolerance':
            self._setTolerance(value)
        else:
            raise AttributeError('unknown property %s' % property.name)

    def do_get_property(self, property):
        if property.name == 'channels':
            return self._channels
        if property.name == 'samplerate':
            return self._samplerate
        if property.name == 'tolerance':
            return self._tolerance
        else:
            raise AttributeError('unknown property %s' % property.name)


class Audioconvert(feedcomponent.PostProcEffect):
    """
    I am an effect that can be added to any component that changes the
    samplerate of the audio output.
    """
    logCategory = "audioconvert-effect"

    def __init__(self, name, sourcePad, pipeline, channels=None,
                 samplerate=None, tolerance=DEFAULT_TOLERANCE,
                 use_audiorate=True):
        """
        @param element:     the video source element on which the post
                            processing effect will be added
        @param sourcePad:   source pad used for linking the effect
        @param pipeline:    the pipeline of the element
        @param channels:    number of output channels
        @param samplerate:  output samplerate
        @param tolerance:   tolerance to correct imperfect timestamps
        """
        feedcomponent.PostProcEffect.__init__(self, name, sourcePad,
            AudioconvertBin(channels, samplerate, tolerance),
                            pipeline)

    def effect_setTolerance(self, tolerance):
        self.effectBin.set_property("tolerance", tolerance)
        return tolerance

    def effect_getTolerance(self):
        return self.effectBin.get_property('tolerance')

    def effect_setSamplerate(self, samplerate):
        self.effectBin.set_property("samplerate", samplerate)
        return samplerate

    def effect_getSamplerate(self):
        return self.effectBin.get_property('samplerate')

    def effect_setChannels(self, channels):
        self.effectBin.set_property("channels", channels)
        return channels

    def effect_getChannels(self):
        return self.effectBin.get_property('channels')
