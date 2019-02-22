#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods
from hamcrest import assert_that
from hamcrest import is_
from hamcrest import is_not
from hamcrest import none

import fudge

from datetime import datetime

from Queue import Queue

from z3c.baseregistry.baseregistry import BaseComponents

from zope.component import globalSiteManager as BASE

from zope.interface.interfaces import IComponents

from nti.appserver.policies.sites import BASEADULT

from nti.contenttypes.calendar.model import CalendarEvent

from nti.contenttypes.calendar.tests import ContentTypesCalendarLayerTest

from nti.contenttypes.calendar.job import generate_executing_time

from nti.dataserver.job.utils import create_and_queue_scheduled_job

from nti.dataserver.tests import mock_dataserver

from nti.dataserver.tests.mock_dataserver import WithMockDS

ALPHA = BaseComponents(BASEADULT,
                       name='alpha.nextthought.com',
                       bases=(BASEADULT,))


class TestJob(ContentTypesCalendarLayerTest):

    def setUp(self):
        super(TestJob, self).setUp()
        ALPHA.__init__(ALPHA.__parent__, name=ALPHA.__name__, bases=ALPHA.__bases__)
        BASE.registerUtility(ALPHA, name=ALPHA.__name__, provided=IComponents)

    def tearDown(self):
        BASE.unregisterUtility(ALPHA, name=ALPHA.__name__, provided=IComponents)
        super(TestJob, self).tearDown()

    def test_generate_executing_time(self):
        event = CalendarEvent(title=u'abc', start_time=datetime.utcfromtimestamp(2800))
        assert_that(generate_executing_time(event), is_(1000))

    @fudge.patch('nti.asynchronous.scheduled.utils.get_scheduled_queue')
    @WithMockDS
    def test_calendar_job(self, fake_queue):
        with mock_dataserver.mock_db_trans(self.ds, site_name='alpha.nextthought.com'):
            queue = Queue()
            fake_queue.is_callable().returns(queue)
            event = CalendarEvent(title=u'abc', start_time=datetime.utcfromtimestamp(2800))
            conn = mock_dataserver.current_transaction
            conn.add(event)
            create_and_queue_scheduled_job(event)
            assert_that(queue.empty(), is_not(True))
            job = queue.get()
            # test it will execute
            job()
            assert_that(job.kwargs['site_name'], is_('alpha.nextthought.com'))
            assert_that(event.ntiid, is_not(none()))
            assert_that(job.kwargs['obj_ntiid'], is_(event.ntiid))
