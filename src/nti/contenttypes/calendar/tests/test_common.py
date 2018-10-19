#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import unittest

from hamcrest import assert_that
from hamcrest import starts_with

from nti.contenttypes.calendar.common import generate_calendar_event_ntiid

class TestCommon(unittest.TestCase):

    def test_generate_calendar_event_ntiid(self):
        ntiid = generate_calendar_event_ntiid()
        assert_that(ntiid, starts_with("tag:nextthought.com,2011-10:NTI-CalendarEvent-system_"))
