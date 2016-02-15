# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# configuration for flumotion's use of epyfilter.py

from epyfilter import Start, Stop, Block

global starts, singles

starts = [
    Start('^=+$', [
        Stop('^$', [
            Block('In gtk'),
            Block('In gobject'),
            Block('In __builtin__'),
            # don't catch only /twisted/ since we have a twisted dir too
            Block('.*/twisted/spread'),
            Block('.*/twisted/trial'),
        ])
    ]),
    Start('- TestResult', [
        Stop('TestCase.run\)$', [
            Block('from twisted.trial'),
        ])
    ]),
    Start('.*\/ihooks.py.*DeprecationWarning: The sre module', [
        Stop('.*return imp.load_source\(name, filename, file\)', [
            Block(None),
        ])
    ]),
    Start('.*epydoc\/uid.py:.*GtkDeprecationWarning', [
        Stop('.*obj not in self._module.value', [
            Block(None),
        ])
    ]),
    Start('.* - twisted\.', [
        Stop('.*\(base method=', [
            Block(None),
        ])
    ]),
    Start('.* - pb.BrokerFactory', [
        Stop('.*\(from twisted.spread.flavors.Root.rootObject\)', [
            Block(None),
        ])
    ]),
    Start('.* - TestResult', [
        Stop('.*\(from twisted.trial.unittest.TestCase.run\)', [
            Block(None),
        ])
    ]),
]

singles = [
    "^Warning: <type 'exceptions\.",
    "^Warning: UID conflict detected: gobject",
    "^Warning: UID conflict detected: __builtin__",
    "^Warning: UID conflict detected: twisted",
    ".*- pb.getObjectAt \(from twisted.spread.flavors.Root\)",
    ".*- Deferred \(from twisted.trial.unittest.TestCase.run\)",
]
