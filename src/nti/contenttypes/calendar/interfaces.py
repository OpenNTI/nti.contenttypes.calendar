#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from zope.container.constraints import contains

from zope.container.interfaces import IContained
from zope.container.interfaces import IContainer

from zope.schema.interfaces import ValidationError

from nti.base.interfaces import ICreated
from nti.base.interfaces import ILastModified
from nti.base.interfaces import ITitledDescribed

from nti.contenttypes.presentation.interfaces import href_schema_field

from nti.schema.field import Text
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine


class ICalendarEvent(ICreated, ILastModified, ITitledDescribed, IContained):
    """
    A calendar event.
    """
    title = ValidTextLine(title=u"Title of the calendar event",
                          min_length=1,
                          required=True)

    description = Text(title=u"Description of the calendar event",
                       required=False)

    location = ValidTextLine(title=u"Location of this event",
                             description=u"Where the calendar event should take place",
                             required=False)

    start_time = ValidDatetime(title=u"This start date",
                                 description=u"""When the calendar event starts. If not provided, will
                                 default to created date.""",
                                 required=True)

    end_time = ValidDatetime(title=u"This end date",
                             description=u"When the calendar event ends.",
                             required=False)

    icon = href_schema_field(title=u"Calendar event icon href",
                             required=False)

    @interface.invariant
    def start_end_time(self):
        "The end time can not before the start time."
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError("The end time can not before the start time.")


class ICalendar(ILastModified, ITitledDescribed, IContainer):
    """
    A storage container for :class:`ICalendarEvent` objects.
    """
    contains(ICalendarEvent)

    title = ValidTextLine(title=u"Title of the calendar",
                          default=u'',
                          required=True)

    description = ValidTextLine(title=u"Description of the calendar",
                                required=False)

    def store_event(event):
        """
        Store the given calendar event into this container.
        """

    def remove_event(event):
        """
        Remove the given event.
        """

    def retrieve_event(event_id):
        """
        Retrieve the potential calendar event with given id.
        """


class ICalendarEventProvider(interface.Interface):
    """
    An intended subscriber provider of possible :class:`ICalendarEvent` objects
    for a :class:`IUser`.
    """

    def iter_events(context_ntiids=None, **kwargs):
        """
        A generator of :class:`ICalendarEvent` objects.
        """


# catalog

class ICalendarContextNTIIDAdapter(interface.Interface):
    """
    Adapts contained objects to their context NTIID.
    """
    contextNTIID = interface.Attribute("NTIID string")


class ICalendarProvider(interface.Interface):
    """
    An intended subscriber provider of possible :class:`ICalendar` objects
    for a :class:`IUser`.
    """

    def iter_calendars():
        """
        A generator of :class:`ICalendar` objects.
        """
