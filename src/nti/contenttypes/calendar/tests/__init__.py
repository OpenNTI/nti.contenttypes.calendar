#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

import unittest

import zope.testing.cleanup

from nti.testing.layers import ConfiguringLayerMixin
from nti.testing.layers import find_test
from nti.testing.layers import ZopeComponentLayer

from nti.dataserver.tests import DSInjectorMixin

from nti.dataserver.tests.mock_dataserver import _TestBaseMixin


class SharedConfiguringTestLayer(ZopeComponentLayer,
                                 ConfiguringLayerMixin,
                                 DSInjectorMixin):

    set_up_packages = ('nti.dataserver',
                       'nti.contenttypes.calendar',)

    @classmethod
    def setUp(cls):
        cls.setUpPackages()

    @classmethod
    def tearDown(cls):
        cls.tearDownPackages()
        zope.testing.cleanup.cleanUp()

    @classmethod
    def testSetUp(cls, test=None):
        test = test or find_test()
        cls.setUpTestDS(test)

    @classmethod
    def testTearDown(cls):
        pass


class ContentTypesCalendarLayerTest(_TestBaseMixin,
                                    unittest.TestCase):
    layer = SharedConfiguringTestLayer
