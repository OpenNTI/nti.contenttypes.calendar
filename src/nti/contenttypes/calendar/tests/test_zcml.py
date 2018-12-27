#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from hamcrest import is_
from hamcrest import is_not
from hamcrest import not_none
from hamcrest import assert_that
from hamcrest import instance_of

from zope import component
from zope.component.hooks import site

from nti.appserver.policies.sites import BASECOPPA as BASESITE

from nti.asynchronous.redis_queue import PriorityQueue
from nti.asynchronous.redis_queue import ScheduledQueue

from nti.contenttypes.calendar import get_scheduled_factory
from nti.contenttypes.calendar import get_notification_factory
from nti.contenttypes.calendar import SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME
from nti.contenttypes.calendar import NOTIFICATION_CALENDAR_EVENTS_QUEUE_NAME

from nti.contenttypes.calendar.interfaces import ICalendarEventScheduledQueueFactory
from nti.contenttypes.calendar.interfaces import ICalendarEventNotificationQueueFactory

from nti.site.transient import TrivialSite as _TrivialSite

from nti.testing.base import ConfiguringTestBase

ZCML_STRING = """
        <configure xmlns="http://namespaces.zope.org/zope"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:calendar="http://nextthought.com/ntp/calendar">

            <include package="z3c.baseregistry" file="meta.zcml" />

            <include package="nti.contenttypes.calendar" file="meta.zcml" />

            <registerIn registry="nti.contenttypes.calendar.tests.test_zcml._TEST_SITE">
                <calendar:registerScheduledQueue />
                <calendar:registerNotificationQueue />
            </registerIn>

        </configure>
        """

from z3c.baseregistry.baseregistry import BaseComponents
_TEST_SITE = BaseComponents(BASESITE, name='test.components', bases=(BASESITE,))


class TestZcml(ConfiguringTestBase):

    def test_zcml(self):
        self.configure_string(ZCML_STRING)
        with site(_TrivialSite(_TEST_SITE)):
            factory = get_scheduled_factory()
            assert_that(ICalendarEventScheduledQueueFactory.providedBy(factory), is_(True))
            queue = factory.get_queue(SCHEDULED_CALENDAR_EVENTS_QUEUE_NAME)
            assert_that(queue, instance_of(ScheduledQueue))

            factory = get_notification_factory()
            assert_that(ICalendarEventNotificationQueueFactory.providedBy(factory), is_(True))
            queue = factory.get_queue(NOTIFICATION_CALENDAR_EVENTS_QUEUE_NAME)
            assert_that(queue, instance_of(PriorityQueue))
