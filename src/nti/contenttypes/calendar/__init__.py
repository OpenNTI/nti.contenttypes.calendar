#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from nti.contenttypes.calendar.interfaces import ICalendarEventScheduledQueueFactory
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationQueueFactory

SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME = '++etc++calendar++queue++calendarevents++scheduled'
SCHEDULED_QUEUE_NAMES = (SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME, )


NOTIFICATION_CALENDAR_EVENTS_QUEUE_NAME = '++etc++calendar++queue++calendarevents++notification'
NOTIFICATION_QUEUE_NAMES = (NOTIFICATION_CALENDAR_EVENTS_QUEUE_NAME, )


def get_scheduled_factory():
    return component.getUtility(ICalendarEventScheduledQueueFactory)


def get_notification_factory():
    return component.getUtility(ICalendarEventNotificationQueueFactory)
