include $(top_srcdir)/common/python.mk

component_PYTHON = __init__.py voaac.py
componentdir = $(libdir)/flumotion/python/flumotion/component/muxers/voaac
component_DATA = \
	voaac.xml

clean-local:
	rm -rf *.pyc *.pyo

EXTRA_DIST = $(component_DATA)
