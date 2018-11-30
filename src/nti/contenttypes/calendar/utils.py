#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from datetime import datetime

from zope import component

from zope.intid.interfaces import IIntIds

from nti.contenttypes.calendar.index import IX_SITE
from nti.contenttypes.calendar.index import IX_START_TIME
from nti.contenttypes.calendar.index import IX_END_TIME
from nti.contenttypes.calendar.index import IX_MIMETYPE
from nti.contenttypes.calendar.index import IX_CONTEXT_NTIID
from nti.contenttypes.calendar.index import get_calendar_event_catalog


MAX_TS = time.mktime(datetime.max.timetuple())


def get_indexed_calendar_events(contexts=None, notBefore=None, notAfter=None, mimeTypes=None, sites=None,
                                catalog=None, intids=None):
    catalog = get_calendar_event_catalog() if catalog is None else catalog
    intids = component.getUtility(IIntIds) if intids is None else intids
    query = {}

    # contexts: like user, course, community, group.
    if contexts:
        if not isinstance(contexts, (list, tuple)):
            contexts = [contexts]
        query[IX_CONTEXT_NTIID] = {'any_of': tuple([getattr(x, 'ntiid', x) for x in contexts])}

    if notBefore:
        query[IX_END_TIME] = {'between': (notBefore, MAX_TS)}

    if notAfter:
        query[IX_START_TIME] = {'between': (0, notAfter)}

    if mimeTypes:
        if not isinstance(mimeTypes, (list, tuple)):
            mimeTypes = [mimeTypes]
        query[IX_MIMETYPE] = {'any_of': tuple(mimeTypes)}

    if sites:
        if not isinstance(sites, (list, tuple)):
            sites = [sites]
        query[IX_SITE] = {'any_of': tuple(sites)}

    result = list()
    if query:
        intids_set = catalog.apply(query)
        for intid in intids_set or ():
            event = intids.getObject(intid)
            result.append(event)

    return result
