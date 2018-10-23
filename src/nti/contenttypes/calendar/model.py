#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface
from zope import lifecycleevent

from zope.cachedescriptors.property import Lazy
from zope.cachedescriptors.property import readproperty

from zope.container.contained import Contained

from zope.location.location import locate

from ZODB.interfaces import IConnection

from nti.containers.containers import CaseInsensitiveCheckingLastModifiedBTreeContainer

from nti.dataserver.authorization_acl import acl_from_aces

from nti.dublincore.datastructures import PersistentCreatedModDateTrackingObject

from nti.property.property import LazyOnClass

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import PermissiveSchemaConfigured as SchemaConfigured

from nti.contenttypes.calendar.interfaces import ICalendar
from nti.contenttypes.calendar.interfaces import ICalendarEvent

from nti.contenttypes.calendar.common import generate_calendar_event_ntiid


@interface.implementer(ICalendarEvent)
class CalendarEvent(SchemaConfigured,
                    PersistentCreatedModDateTrackingObject,
                    Contained):

    __external_can_create__ = True

    createDirectFieldProperties(ICalendarEvent)

    mimeType = mime_type = "application/vnd.nextthought.calendar.calendarevent"

    @LazyOnClass
    def __acl__(self):
        # If we don't have this, it would derive one from ICreated,
        # rather than its parent (ICalendar).
        return acl_from_aces([])

    def __init__(self, *args, **kwargs):
        SchemaConfigured.__init__(self, *args, **kwargs)
        PersistentCreatedModDateTrackingObject.__init__(self)

    @Lazy
    def ntiid(self):
        return generate_calendar_event_ntiid()

    @readproperty
    def start_time(self):
        return self.created


def save_in_container(container, key, value, event=True):
    if event:
        container[key] = value
    else:
        # avoid dublincore annotations for performance
        container._setitemf(key, value)
        locate(value, parent=container, name=key)
        if      IConnection(container, None) is not None \
            and IConnection(value, None) is None:
            IConnection(container).add(value)
        lifecycleevent.added(value, container, key)
        try:
            container.updateLastMod()
        except AttributeError:
            pass
        container._p_changed = True
    return value


@interface.implementer(ICalendar)
class Calendar(CaseInsensitiveCheckingLastModifiedBTreeContainer, SchemaConfigured):

    __external_can_create__ = False

    mimeType = mime_type = "application/vnd.nextthought.calendar.calendar"

    createDirectFieldProperties(ICalendar)

    creator = None

    def __init__(self, *args, **kwargs):
        CaseInsensitiveCheckingLastModifiedBTreeContainer.__init__(self)
        SchemaConfigured.__init__(self, *args, **kwargs)

    def store_event(self, event):
        return save_in_container(self, event.ntiid, event)

    def remove_event(self, event):
        ntiid = getattr(event, 'ntiid', event)
        del self[ntiid]

    def retrieve_event(self, ntiid):
        assert ntiid, "Must provide a ntiid."
        return self.get(ntiid, None)
