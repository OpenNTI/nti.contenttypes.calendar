#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import component
from zope import interface

from zope.cachedescriptors.property import Lazy
from zope.cachedescriptors.property import readproperty

from zope.container.contained import Contained

from zope.container.interfaces import INameChooser

from nti.asynchronous.scheduled.job import ScheduledJob

from nti.containers.containers import AbstractNTIIDSafeNameChooser
from nti.containers.containers import CaseInsensitiveCheckingLastModifiedBTreeContainer

from nti.dublincore.datastructures import PersistentCreatedModDateTrackingObject

from nti.ntiids.oids import to_external_ntiid_oid

from nti.property.property import alias

from nti.schema.fieldproperty import AdaptingFieldProperty
from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import PermissiveSchemaConfigured as SchemaConfigured

from nti.contenttypes.calendar.interfaces import ICalendar
from nti.contenttypes.calendar.interfaces import ICalendarEvent
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationJob


@interface.implementer(ICalendarEvent)
class CalendarEvent(SchemaConfigured,
                    PersistentCreatedModDateTrackingObject,
                    Contained):

    __external_can_create__ = True

    createDirectFieldProperties(ICalendarEvent)

    start_time = AdaptingFieldProperty(ICalendarEvent['start_time'])

    end_time = AdaptingFieldProperty(ICalendarEvent['end_time'])

    mimeType = mime_type = "application/vnd.nextthought.calendar.calendarevent"

    id = alias('__name__')

    def __init__(self, *args, **kwargs):
        SchemaConfigured.__init__(self, *args, **kwargs)
        PersistentCreatedModDateTrackingObject.__init__(self)

    @readproperty
    def start_time(self):
        return self.created

    @Lazy
    def ntiid(self):
        return to_external_ntiid_oid(self)

    @readproperty
    def containerId(self):
        if self.__parent__ is not None:
            return self.__parent__.ntiid


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
        if not getattr(event, 'id', None):
            event.id = INameChooser(self).chooseName(event.title, event)
        self[event.id] = event
        return event

    def remove_event(self, event):
        key = getattr(event, 'id', event)
        try:
            del self[key]
            result = True
        except KeyError:
            result = False
        return result

    def retrieve_event(self, event_id):
        return self.get(event_id, None)

    @Lazy
    def ntiid(self):
        return to_external_ntiid_oid(self)


@component.adapter(ICalendar)
@interface.implementer(INameChooser)
class _CalendarNameChooser(AbstractNTIIDSafeNameChooser):
    """
    Handles NTIID-safe name choosing for a calendar event.
    """
    leaf_iface = ICalendar


@interface.implementer(ICalendarEventNotificationJob)
class CalendarEventNotificationJob(ScheduledJob):
    pass
