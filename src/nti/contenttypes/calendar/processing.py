#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
import calendar

from zope import component

from zope.component.hooks import getSite
from zope.component.hooks import site as current_site

from nti.asynchronous.job import create_scheduled_job

from nti.contenttypes.calendar import get_scheduled_factory
from nti.contenttypes.calendar import get_notification_factory
from nti.contenttypes.calendar import SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME
from nti.contenttypes.calendar import NOTIFICATION_CALENDAR_EVENTS_QUEUE_NAME

from nti.contenttypes.calendar.interfaces import ICalendarEvent
from nti.contenttypes.calendar.interfaces import ICalendarEventNotifier
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationValidator

from nti.contenttypes.calendar.model import CalendarEventNotificationJob

from nti.dataserver.interfaces import IDataserver

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.site.site import get_site_for_site_names

from nti.site.transient import TrivialSite

SCORE_INTERVAL = 30*60


def generate_score(calendar_event):
    dt = calendar_event.start_time
    return calendar.timegm(dt.utctimetuple()) - SCORE_INTERVAL


def get_site(site_name=None):
    if site_name is None:
        site = getSite()
        site_name = site.__name__ if site is not None else None
    return site_name


def get_scheduled_queue(name):
    factory = get_scheduled_factory()
    return factory.get_queue(name)


def put_job(name, func, jid, *args, **kwargs):
    queue = get_scheduled_queue(name)
    job = create_scheduled_job(func,
                               jobid=jid,
                               score=kwargs['original_score'],
                               jargs=args,
                               jkwargs=kwargs,
                               cls=CalendarEventNotificationJob)
    queue.put(job)
    return job


def add_to_queue(name, func, calendar_event, next_func, jid=None):
    site = get_site()
    ntiid = calendar_event.ntiid
    if ntiid and site:
        jid = '%s_%s_%s' % (ntiid, jid, time.time())
        next_jid = '%s_%s' % (jid, 'notification')
        original_score = generate_score(calendar_event)

        return put_job(name, func, jid,
                       site=site,
                       next_jid=next_jid,
                       next_func=next_func,
                       original_score=original_score,
                       event_ntiid=ntiid)
    return None


def queue_add(calendar_event):
    return add_to_queue(SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME,
                        _execute_scheduled_job,
                        calendar_event,
                        jid='added',
                        next_func=_execute_notification_job)


def queue_modified(calendar_event):
    return add_to_queue(SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME,
                        _execute_scheduled_job,
                        calendar_event,
                        jid='modified',
                        next_func=_execute_notification_job)


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


def get_notification_queue(name):
    factory = get_notification_factory()
    return factory.get_queue(name)


def _execute_scheduled_job(next_func, next_jid, *args, **kwargs):
    queue = get_notification_queue(NOTIFICATION_CALENDAR_EVENTS_QUEUE_NAME)
    job = create_scheduled_job(next_func,
                              jobid=next_jid,
                              score=kwargs['original_score'],
                              jargs=args,
                              jkwargs=kwargs,
                              cls=CalendarEventNotificationJob)
    queue.put(job)
    return job


def _execute_notification_job(event_ntiid, original_score, site=None, *args, **kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = find_object_with_ntiid(event_ntiid)
        if not ICalendarEvent.providedBy(obj):
            return

        validator = ICalendarEventNotificationValidator(obj, None)
        if validator and not validator.validate(original_score=original_score):
            return

        notifier = ICalendarEventNotifier(obj, None)
        if notifier:
            notifier.notify()
