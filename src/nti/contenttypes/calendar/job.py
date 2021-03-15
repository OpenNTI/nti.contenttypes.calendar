#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.contenttypes.calendar.interfaces import ICalendarEvent
from nti.contenttypes.calendar.interfaces import ICalendarEventNotifier
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationValidator
from nti.contenttypes.calendar.interfaces import ICalendarEventURLProvider

from nti.contenttypes.calendar.utils import generate_executing_time

from nti.dataserver.job.decorators import RunJobInSite

from nti.dataserver.job.job import AbstractJob

from nti.dataserver.job.interfaces import IScheduledJob

from nti.ntiids.ntiids import find_object_with_ntiid

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IScheduledJob)
class CalendarScheduledNotificationJob(AbstractJob):

    def __init__(self, calendar_event):
        super(CalendarScheduledNotificationJob, self).__init__(calendar_event)
        self.job_id_prefix = calendar_event.ntiid
        self.execution_time = generate_executing_time(calendar_event)
        provider = ICalendarEventURLProvider(calendar_event, None)
        event_url = provider() if provider else None
        self.job_kwargs['event_url'] = event_url

    @RunJobInSite
    def __call__(self, *args, **kwargs):
        obj_ntiid = kwargs.get('obj_ntiid')
        event = find_object_with_ntiid(obj_ntiid)
        if not ICalendarEvent.providedBy(event):
            logger.warning("Ignoring the processing of calendar event job,"
                           " {0} is not a calendar event or was deleted.".format(event or obj_ntiid))
            return

        validator = ICalendarEventNotificationValidator(event, None)
        if validator and not validator.validate(original_executing_time=self.execution_time):
            logger.warning("Ignoring the processing of outdated calendar event job. event_ntiid={0}".format(obj_ntiid))
            return

        notifier = ICalendarEventNotifier(event, None)
        if notifier:
            notifier.notify(event_url=kwargs.pop('event_url', None))
