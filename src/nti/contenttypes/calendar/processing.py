#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

logger = __import__('logging').getLogger(__name__)

import time
import calendar

from zope import component

from zope.component.hooks import getSite
from zope.component.hooks import site as current_site

from nti.asynchronous.scheduled.job import create_scheduled_job

from nti.asynchronous.scheduled.utils import add_scheduled_job

from nti.contenttypes.calendar.interfaces import ICalendarEvent
from nti.contenttypes.calendar.interfaces import ICalendarEventNotifier
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationValidator
from nti.contenttypes.calendar.interfaces import ICalendarEventURLProvider

from nti.contenttypes.calendar.model import CalendarEventNotificationJob

from nti.dataserver.interfaces import IDataserver

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.site.site import get_site_for_site_names

from nti.site.transient import TrivialSite

EXECUTING_TIME_INTERVAL = 30*60


def generate_executing_time(calendar_event):
    dt = calendar_event.start_time
    return calendar.timegm(dt.utctimetuple()) - EXECUTING_TIME_INTERVAL


def get_site(site_name=None):
    if site_name is None:
        site = getSite()
        site_name = site.__name__ if site is not None else None
    return site_name


def put_job(func, jid, *args, **kwargs):
    job = create_scheduled_job(func,
                               jobid=jid,
                               timestamp=kwargs['original_executing_time'],
                               jargs=args,
                               jkwargs=kwargs,
                               cls=CalendarEventNotificationJob)
    return add_scheduled_job(job)


def add_to_queue(func, calendar_event, jid=None):
    site = get_site()
    ntiid = calendar_event.ntiid
    if ntiid and site:
        jid = '%s_%s_%s' % (ntiid, jid, time.time())
        original_executing_time = generate_executing_time(calendar_event)

        provider = ICalendarEventURLProvider(calendar_event, None)
        event_url = provider() if provider else None

        return put_job(func,
                       jid,
                       site=site,
                       original_executing_time=original_executing_time,
                       event_ntiid=ntiid,
                       event_url=event_url)
    return None


def queue_add(calendar_event):
    return add_to_queue(_execute_notification_job,
                        calendar_event,
                        jid='added')


def queue_modified(calendar_event):
    return add_to_queue(_execute_notification_job,
                        calendar_event,
                        jid='modified')


# job functions


def get_job_site(job_site_name=None):
    old_site = getSite()
    if job_site_name is None:
        job_site = old_site
    else:
        dataserver = component.getUtility(IDataserver)
        ds_folder = dataserver.root_folder['dataserver2']
        with current_site(ds_folder):
            job_site = get_site_for_site_names((job_site_name,))

        if job_site is None or isinstance(job_site, TrivialSite):
            raise ValueError('No site found for (%s)' % job_site_name)
    return job_site


def _execute_notification_job(event_ntiid, original_executing_time, site=None, *args, **kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = find_object_with_ntiid(event_ntiid)
        if not ICalendarEvent.providedBy(obj):
            logger.warning("Ignoring the processing of calendar event job, {0} is not a calendar event or was deleted.".format(obj or event_ntiid))
            return

        validator = ICalendarEventNotificationValidator(obj, None)
        if validator and not validator.validate(original_executing_time=original_executing_time):
            logger.warning("Ignoring the processing of outdated calendar event job. event_ntiid={0}".format(event_ntiid))
            return

        notifier = ICalendarEventNotifier(obj, None)
        if notifier:
            notifier.notify(event_url=kwargs.pop('event_url', None))
