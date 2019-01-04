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

from nti.contenttypes.calendar.model import CalendarEvent

from nti.contenttypes.calendar.tests import ContentTypesCalendarLayerTest

from nti.contenttypes.calendar.processing import generate_score


class TestProcessing(ContentTypesCalendarLayerTest):

    def test_generate_score(self):
        event = CalendarEvent(title=u'abc', start_time=datetime.utcfromtimestamp(2800))
        assert_that(generate_score(event), is_(1000))
