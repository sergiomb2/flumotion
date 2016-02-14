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

from gi.repository import Gst

from flumotion.common import gstreamer
from flumotion.component import feedcomponent
from vorbisutils import get_max_sample_rate, get_preferred_sample_rate

__version__ = "$Rev$"


class Vorbis(feedcomponent.EncoderComponent):
    checkTimestamp = True
    checkOffset = True

    def do_check(self):
        self.debug('running Vorbis check')
        from flumotion.worker.checks import encoder
        d = encoder.checkVorbis()

        d.addCallback(self._checkCallback)

        return d

    def _checkCallback(self, result):
        for m in result.messages:
            self.addMessage(m)

    def get_pipeline_string(self, properties):
        self.bitrate = properties.get('bitrate', -1)
        self.quality = properties.get('quality', 0.3)
        self.channels = properties.get('channels', 2)
        resampler = 'audioresample'
        if gstreamer.element_factory_exists('legacyresample'):
            resampler = 'legacyresample'
        return ('%s name=ar ! audioconvert ! capsfilter name=cf '
                '! vorbisenc name=encoder' % resampler)

    def configure_pipeline(self, pipeline, properties):
        enc = pipeline.get_by_name('encoder')
        cf = pipeline.get_by_name('cf')
        ar = pipeline.get_by_name('ar')

        assert enc and cf and ar

        if self.bitrate > -1:
            enc.set_property('bitrate', self.bitrate)
        else:
            enc.set_property('quality', self.quality)

        pad = ar.get_static_pad('sink')
        handle = None

        def buffer_probe(pad, buffer, user_data):
            # this comes from another thread
            caps = pad.get_current_caps()
            in_rate = caps.get_structure(0).get_int('rate')[1]

            # now do necessary filtercaps
            self.rate = in_rate
            if self.bitrate > -1:
                maxsamplerate = get_max_sample_rate(
                    self.bitrate, self.channels)
                if in_rate > maxsamplerate:
                    self.rate = get_preferred_sample_rate(maxsamplerate)
                    self.debug(
                        'rate %d > max rate %d (for %d kbit/sec), '
                        'selecting rate %d instead' % (
                        in_rate, maxsamplerate, self.bitrate, self.rate))


            caps_str = 'audio/x-raw, rate=%d, channels=%d' % (self.rate,
                        self.channels)
            cf.set_property('caps',
                            Gst.Caps.from_string(caps_str))
            pad.remove_probe(handle)
            return True

        handle = pad.add_probe(Gst.PadProbeType.BUFFER, buffer_probe, None)

    def modify_property_Bitrate(self, value):
        if not self.checkPropertyType('bitrate', value, int):
            return False
        maxsamplerate = get_max_sample_rate(value, self.channels)
        if self.rate > maxsamplerate:
            self.warning("Could not set property 'bitrate' on the theora "
                "encoder: rate %d > max rate %d (for %d kbit/sec)" % (
                self.rate, maxsamplerate, value))
            return False
        self.modify_element_property('enc', 'bitrate', value, needs_reset=True)
        return True
