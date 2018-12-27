#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from datetime import datetime

from hamcrest import is_
from hamcrest import not_none
from hamcrest import assert_that
from hamcrest import instance_of
from hamcrest import has_length

from zope import component

from nti.contenttypes.calendar import get_scheduled_factory
from nti.contenttypes.calendar import get_notification_factory

from nti.contenttypes.calendar.model import CalendarEvent

from nti.contenttypes.calendar.tests import ContentTypesCalendarLayerTest

from nti.contenttypes.calendar.interfaces import ICalendarEventScheduledQueueFactory
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationQueueFactory

from nti.contenttypes.calendar.processing import generate_score
from nti.contenttypes.calendar.processing import get_scheduled_queue

from nti.contenttypes.calendar.zcml import ImmediateQueueRunner

class TestProcessing(ContentTypesCalendarLayerTest):

    def test_queues(self):
        factory = get_scheduled_factory()
        assert_that(factory, not_none())
        assert_that(ICalendarEventScheduledQueueFactory.providedBy(factory), is_(True))
        assert_that(factory.get_queue(None), instance_of(ImmediateQueueRunner))

        factory = get_notification_factory()
        assert_that(factory, not_none())
        assert_that(ICalendarEventNotificationQueueFactory.providedBy(factory), is_(True))
        assert_that(factory.get_queue(None), instance_of(ImmediateQueueRunner))

    def test_generate_score(self):
        event = CalendarEvent(title=u'abc', start_time=datetime.utcfromtimestamp(2800))
        assert_that(generate_score(event), is_(1000))
