#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope import component
from zope import interface

from zope.annotation import factory as an_factory

from zope.security.interfaces import IPrincipal

from nti.containers.containers import CaseInsensitiveCheckingLastModifiedBTreeContainer

from nti.contenttypes.calendar.interfaces import ICalendarEvent
from nti.contenttypes.calendar.interfaces import ICalendarEventAttendanceContainer
from nti.contenttypes.calendar.interfaces import IUserCalendarEventAttendance

from nti.dublincore.datastructures import PersistentCreatedModDateTrackingObject

from nti.property.property import alias

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IUserCalendarEventAttendance)
class UserCalendarEventAttendance(SchemaConfigured,
                                  PersistentCreatedModDateTrackingObject):
    createDirectFieldProperties(IUserCalendarEventAttendance)

    __parent__ = None

    mimeType = mime_type = "application/vnd.nextthought.calendar.usercalendareventattendance"

    Username = alias('__name__')


@component.adapter(ICalendarEvent)
@interface.implementer(ICalendarEventAttendanceContainer)
class CalendarEventAttendanceContainer(CaseInsensitiveCheckingLastModifiedBTreeContainer,
                                       SchemaConfigured):
    createDirectFieldProperties(IUserCalendarEventAttendance)

    def add_attendance(self, user, attendance):
        id = IPrincipal(user).id
        self[id] = attendance
        return attendance

    def remove_attendance(self, user):
        id = IPrincipal(user).id
        try:
            del self[id]
            result = True
        except KeyError:
            result = False
        return result


CalendarEventAttendanceContainerFactory = an_factory(CalendarEventAttendanceContainer,
                                                     u'EventAttendance')
