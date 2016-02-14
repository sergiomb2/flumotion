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

from flumotion.common import errors, gstreamer, messages
from flumotion.common.i18n import N_, gettexter
from flumotion.component import feedcomponent

__version__ = "$Rev$"
T_ = gettexter()


class VideoTestMedium(feedcomponent.FeedComponentMedium):

    def remote_setPattern(self, pattern):
        return self.comp.set_element_property('source', 'pattern',
                                              pattern)


class VideoTest(feedcomponent.ParseLaunchComponent):
    componentMediumClass = VideoTestMedium

    def init(self):
        self.uiState.addKey('pattern', 0)

    def get_pipeline_string(self, properties):
        capsString = properties.get('format', 'video/x-raw')

        if capsString == 'video/x-raw':
            capsString = '%s,format=(string)I420' % capsString

        # Filtered caps
        struct = Gst.structure_from_string(capsString)[0]
        for k in 'width', 'height':
            if k in properties:
                struct.set_value(k, properties[k])

        if 'framerate' in properties:
            framerate = properties['framerate']
            struct.set_value('framerate', Gst.Fraction(framerate[0]/framerate[1]))

        # always set par
        struct.set_value('pixel-aspect-ratio', Gst.Fraction(1/1))
        if 'pixel-aspect-ratio' in properties:
            par = properties['pixel-aspect-ratio']
            struct.set_value('pixel-aspect-ratio', Gst.Fraction(par[0]/par[1]))

        # If RGB, set something ffmpegcolorspace can convert.
        if capsString == 'video/x-raw-rgb':
            struct.set_value('red_mask', 0xff00)
        caps = Gst.Caps.from_string(struct.to_string())

        is_live = 'is-live=true'

        overlay = ""
        overlayTimestamps = properties.get('overlay-timestamps', False)
        if overlayTimestamps:
            overlay = " timeoverlay ! "

        return "videotestsrc %s name=source ! " % is_live + overlay + \
            "identity name=identity silent=TRUE ! %s" % caps

    # Set properties

    def configure_pipeline(self, pipeline, properties):

        def notify_pattern(obj, pspec):
            self.uiState.set('pattern', int(obj.get_property('pattern')))

        source = self.get_element('source')
        source.connect('notify::pattern', notify_pattern)
        if 'pattern' in properties:
            source.set_property('pattern', properties['pattern'])

        if 'drop-probability' in properties:
            vt = gstreamer.get_plugin_version('coreelements')
            if not vt:
                raise errors.MissingElementError('identity')
            if not vt > (0, 10, 12, 0):
                self.addMessage(
                    messages.Warning(T_(N_(
                        "The 'drop-probability' property is specified, but "
                        "it only works with GStreamer core newer than 0.10.12."
                        " You should update your version of GStreamer."))))
            else:
                drop_probability = properties['drop-probability']
                if drop_probability < 0.0 or drop_probability > 1.0:
                    self.addMessage(
                        messages.Warning(T_(N_(
                            "The 'drop-probability' property can only be "
                            "between 0.0 and 1.0."))))
                else:
                    identity = self.get_element('identity')
                    identity.set_property('drop-probability',
                        drop_probability)
