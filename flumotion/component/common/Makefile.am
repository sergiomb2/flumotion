include $(top_srcdir)/common/python.mk

commondir = $(libdir)/flumotion/python/flumotion/component/common
common_DATA =
common_PYTHON = \
	__init__.py

TAGS_FILES = $(common_PYTHON)

clean-local:
	rm -rf *.pyc *.pyo


SUBDIRS = \
	avproducer \
	fgdp \
	streamer

EXTRA_DIST = $(common_DATA)
