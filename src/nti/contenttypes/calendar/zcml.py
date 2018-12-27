#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.component.zcml import utility

from nti.asynchronous import get_job_queue as async_queue

from nti.asynchronous.interfaces import IRedisQueue

from nti.asynchronous.redis_queue import PriorityQueue as RedisQueue
from nti.asynchronous.redis_queue import ScheduledQueue

from nti.contenttypes.calendar import NOTIFICATION_QUEUE_NAMES
from nti.contenttypes.calendar import SCHEDULED_QUEUE_NAMES

from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationQueueFactory
from nti.contenttypes.calendar.interfaces import ICalendarEventScheduledQueueFactory

from nti.coremetadata.interfaces import IRedisClient

logger = __import__('logging').getLogger(__name__)


class ImmediateQueueRunner(object):
    """
    A queue that immediately runs the given job. This is generally
    desired for test or dev mode.
    """
    def put(self, job):
        job()


class _AbstractQueueFactory(object):

    queue_interface = None

    def get_queue(self, name):
        queue = async_queue(name, self.queue_interface)
        if queue is None:
            msg = "No queue exists for calendar events queue (%s)." % name
            raise ValueError(msg)
        return queue

    def _redis(self):
        return component.getUtility(IRedisClient)


# scheduled queue


@interface.implementer(ICalendarEventScheduledQueueFactory)
class _CalendarEventScheduledQueueFactory(_AbstractQueueFactory):

    queue_interface = IRedisQueue

    def __init__(self, _context):
        for name in SCHEDULED_QUEUE_NAMES:
            queue = ScheduledQueue(self._redis, name)
            utility(_context, provides=IRedisQueue, component=queue, name=name)


@interface.implementer(ICalendarEventScheduledQueueFactory)
class _ImmediateScheduledQueueFactory(object):

    def get_queue(self, unused_name):
        return ImmediateQueueRunner()


def registerScheduledQueue(_context):
    logger.info("Registering calendar events scheduled redis queue")
    factory = _CalendarEventScheduledQueueFactory(_context)
    utility(_context, provides=ICalendarEventScheduledQueueFactory, component=factory)


def registerImmediateScheduledQueue(_context):
    logger.info("Registering immediate calendar events scheduled queue")
    factory = _ImmediateScheduledQueueFactory()
    utility(_context, provides=ICalendarEventScheduledQueueFactory, component=factory)


# notification queue


@interface.implementer(ICalendarEventNotificationQueueFactory)
class _CalendarEventNotificationQueueFactory(_AbstractQueueFactory):

    queue_interface = IRedisQueue

    def __init__(self, _context):
        for name in NOTIFICATION_QUEUE_NAMES:
            queue = RedisQueue(self._redis, name)
            utility(_context, provides=IRedisQueue, component=queue, name=name)


@interface.implementer(ICalendarEventNotificationQueueFactory)
class _ImmediateNotificationQueueFactory(object):

    def get_queue(self, unused_name):
        return ImmediateQueueRunner()


def registerNotificationQueue(_context):
    logger.info("Registering calendar events notification redis queue")
    factory = _CalendarEventNotificationQueueFactory(_context)
    utility(_context, provides=ICalendarEventNotificationQueueFactory, component=factory)


def registerImmediateNotificationQueue(_context):
    logger.info("Registering immediate calendar events notification queue")
    factory = _ImmediateNotificationQueueFactory()
    utility(_context, provides=ICalendarEventNotificationQueueFactory, component=factory)
