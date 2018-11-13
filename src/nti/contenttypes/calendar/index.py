#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import BTrees

from zope import component
from zope import interface

from zope.catalog.interfaces import ICatalog

from zope.intid.interfaces import IIntIds

from zope.location import locate

from nti.base._compat import text_

from nti.site.interfaces import IHostPolicyFolder

from nti.zope_catalog.catalog import Catalog

from nti.zope_catalog.index import AttributeValueIndex
from nti.zope_catalog.index import NormalizationWrapper
from nti.zope_catalog.index import IntegerValueIndex as RawIntegerValueIndex

from nti.zope_catalog.datetime import TimestampToNormalized64BitIntNormalizer

from nti.contenttypes.calendar.interfaces import ICalendarEvent


CALENDAR_EVENT_CATALOG_NAME = 'nti.dataserver.++etc++calendar-event-catalog'

#: Site
IX_SITE = 'site'

#: MimeType
IX_MIMETYPE = 'mimeType'

# Context, may include user, course, community, DFL
IX_CONTEXT_NTIID = 'contextNTIID'

#: Start time
IX_START_TIME = 'startTime'

#: End time
IX_END_TIME = 'endTime'


class SiteAdapter(object):

    __slots__ = (b'site',)

    def __init__(self, obj, default=None):
        if not ICalendarEvent.providedBy(obj):
            return

        folder = IHostPolicyFolder(obj, None)
        if folder is not None:
            self.site = text_(folder.__name__)

    def __reduce__(self):
        raise TypeError()


class MimeTypeAdapter(object):

    __slots__ = (b'mimeType',)

    def __init__(self, obj, default=None):
        if not ICalendarEvent.providedBy(obj):
            return
        self.mimeType = getattr(obj, 'mimeType', None) or getattr(obj, 'mime_type', None)

    def __reduce__(self):
        raise TypeError()


class ContextNTIIDAdapter(object):

    __slots__ = (b'contextNTIID',)

    def __init__(self, obj, default=None):
        if not ICalendarEvent.providedBy(obj):
            return

        context = getattr(obj.__parent__, '__parent__', None)
        if context is not None:
            self.contextNTIID = getattr(context, 'ntiid', None)

    def __reduce__(self):
        raise TypeError()


class StartTimeAdapter(object):

    __slots__ = (b'startTime',)

    def __init__(self, obj, default=None):
        if not ICalendarEvent.providedBy(obj):
            return
        if obj.start_time is not None:
            self.startTime = obj.start_time

    def __reduce__(self):
        raise TypeError()


class EndTimeAdapter(object):

    __slots__ = (b'endTime',)

    def __init__(self, obj, default=None):
        if not ICalendarEvent.providedBy(obj):
            return
        if obj.end_time is not None:
            self.endTime = obj.end_time

    def __reduce__(self):
        raise TypeError()


class SiteIndex(AttributeValueIndex):
    default_field_name = IX_SITE
    default_interface = SiteAdapter


class MimeTypeIndex(AttributeValueIndex):
    default_field_name = IX_MIMETYPE
    default_interface = MimeTypeAdapter


class ContextNTIIDIndex(AttributeValueIndex):
    default_field_name = IX_CONTEXT_NTIID
    default_interface = ContextNTIIDAdapter


def StartTimeIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name=IX_START_TIME,
                                interface=StartTimeAdapter,
                                index=RawIntegerValueIndex(family=family),
                                normalizer=TimestampToNormalized64BitIntNormalizer())


def EndTimeIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name=IX_END_TIME,
                                interface=EndTimeAdapter,
                                index=RawIntegerValueIndex(family=family),
                                normalizer=TimestampToNormalized64BitIntNormalizer())


@interface.implementer(ICatalog)
class CalendarEventCatalog(Catalog):
    pass


def get_calendar_event_catalog(lsm=component):
    return lsm.getUtility(ICatalog, name=CALENDAR_EVENT_CATALOG_NAME)


def install_calendar_event_catalog(site_manager_container, intids=None):
    lsm = site_manager_container.getSiteManager()
    intids = lsm.getUtility(IIntIds) if intids is None else intids
    catalog = lsm.queryUtility(ICatalog, name=CALENDAR_EVENT_CATALOG_NAME)
    if catalog is not None:
        return catalog

    catalog = CalendarEventCatalog(family=intids.family)
    locate(catalog, site_manager_container, CALENDAR_EVENT_CATALOG_NAME)
    intids.register(catalog)
    lsm.registerUtility(catalog, provided=ICatalog, name=CALENDAR_EVENT_CATALOG_NAME)

    for name, clazz in ((IX_SITE, SiteIndex),
                        (IX_START_TIME, StartTimeIndex),
                        (IX_END_TIME, EndTimeIndex),
                        (IX_MIMETYPE, MimeTypeIndex),
                        (IX_CONTEXT_NTIID, ContextNTIIDIndex)):
        index = clazz(family=intids.family)
        intids.register(index)
        locate(index, catalog, name)
        catalog[name] = index

    return catalog
