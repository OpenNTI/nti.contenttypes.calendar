#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import datetime

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import contains
from hamcrest import has_entries
from hamcrest import has_length
from hamcrest import has_properties
from hamcrest import is_
from hamcrest import not_none
from hamcrest import raises
from hamcrest import same_instance

from zope.schema.interfaces import ValidationError

from nti.contenttypes.calendar.model import Calendar
from nti.contenttypes.calendar.model import CalendarEvent

from nti.contenttypes.calendar.interfaces import ICalendarEvent

from nti.contenttypes.calendar.tests import ContentTypesCalendarLayerTest

from nti.externalization import internalization

from nti.externalization.externalization import toExternalObject


class TestExternalization(ContentTypesCalendarLayerTest):

    def _internalize(self, external, context=None, factory_=not_none()):
        factory = internalization.find_factory_for(external)
        assert_that(factory, is_(factory_))
        new_io = context if context is not None else (factory() if factory else None)
        if new_io is not None:
            internalization.update_from_external_object(new_io, external)
        return new_io

    def testCalendarEvent(self):
        now = datetime.datetime.utcnow()
        obj =  CalendarEvent(title=u'reading',
                             description=u'this is',
                             location=u'oklahoma',
                             end_time=now,
                             icon=u'/abc/efg')
        assert_that(obj.start_time, is_(obj.created))

        external = toExternalObject(obj)
        assert_that(external, has_entries({'title': 'reading',
                                           'description': 'this is',
                                           'location': 'oklahoma',
                                           'start_time': not_none(),
                                           'end_time': not_none(),
                                           'icon': '/abc/efg',
                                           'Last Modified': not_none(),
                                           'MimeType': 'application/vnd.nextthought.calendar.calendarevent'}))

        new_io = self._internalize(external)
        assert_that(new_io, has_properties({'title': 'reading',
                                            'description': 'this is',
                                            'location': 'oklahoma',
                                            'start_time': not_none(),
                                            'end_time': not_none(),
                                            'icon': '/abc/efg',
                                            'lastModified': not_none()}))


        external = {'title': 'ok', 'start_time': 1539993665, 'end_time': 1543190475,
                    'MimeType': 'application/vnd.nextthought.calendar.calendarevent'}
        new_io = self._internalize(external)
        assert_that(new_io, has_properties({'title': 'ok',
                                           'start_time': not_none(),
                                           'end_time': not_none()}))
        assert_that(new_io.start_time.strftime('%Y-%m-%d %H:%M:%S'), is_('2018-10-20 00:01:05'))
        assert_that(new_io.end_time.strftime('%Y-%m-%d %H:%M:%S'), is_('2018-11-26 00:01:15'))

        external = {'title': 'ok', 'MimeType': 'application/vnd.nextthought.calendar.calendarevent'}
        new_io = self._internalize(external)
        assert_that(new_io.end_time, is_(None))

        obj =  CalendarEvent(title=u'reading', start_time=datetime.datetime.utcfromtimestamp(10), end_time=None)
        ICalendarEvent.validateInvariants(obj)

        obj =  CalendarEvent(title=u'reading', start_time=datetime.datetime.utcfromtimestamp(10), end_time=datetime.datetime.utcfromtimestamp(10))
        ICalendarEvent.validateInvariants(obj)

        obj =  CalendarEvent(title=u'reading', start_time=datetime.datetime.utcfromtimestamp(10), end_time=datetime.datetime.utcfromtimestamp(20))
        ICalendarEvent.validateInvariants(obj)

        obj =  CalendarEvent(title=u'reading', start_time=datetime.datetime.utcfromtimestamp(20), end_time=datetime.datetime.utcfromtimestamp(10))
        assert_that(calling(ICalendarEvent.validateInvariants).with_args(obj), raises(ValidationError, 'The end time can not come before the start time.'))

    def testCalendar(self):
        obj = Calendar(title=u"today", description=u'let us go')
        external = toExternalObject(obj)
        assert_that(external, has_entries({'title': 'today',
                                           'description': 'let us go',
                                           "MimeType": "application/vnd.nextthought.calendar.calendar"}))

        external = {'title': u'future', 'description': 'do not go'}
        new_obj = self._internalize(external, obj, factory_=None)
        assert_that(new_obj, same_instance(obj))
        assert_that(new_obj, has_properties({'title': 'future', 'description': 'do not go'}))

        assert_that(self._internalize(external, factory_=None), is_(None))


class TestContainer(ContentTypesCalendarLayerTest):

    def testCalendar(self):
        event = CalendarEvent(title="english")
        assert_that(event.__parent__, is_(None))

        calendar = Calendar(title=u'study', descrption=None)

        assert_that(calendar.store_event(event), same_instance(event))
        assert_that(calendar.retrieve_event(event.id), same_instance(event))
        assert_that(calendar, has_length(1))
        assert_that([x for x in calendar.values()], contains(event))

        assert_that(event.__parent__, same_instance(calendar))

        calendar.remove_event(event.id)
        assert_that(event.__parent__, is_(None))
        assert_that(calendar.retrieve_event(event.id), is_(None))
        assert_that(calendar, has_length(0))

        assert_that(calendar.store_event(event), same_instance(event))
        assert_that(calendar, has_length(1))
        assert_that(calendar.remove_event(event), is_(True))
        assert_that(calendar, has_length(0))
        assert_that(calendar.remove_event(event), is_(False))
