# -*- coding: utf-8 -*-
#
#   test_changes.py — Changes class test cases
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

"""
Changes class test cases.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

from unittest import TestCase

from debexpo.lib.changes import Changes

class TestChangesController(TestCase):

    def __init__(self, methodName):
        """
        Class constructor. Starts a Changes class for use in other tests.
        """
        TestCase.__init__(self, methodName)

        self.changes = Changes(filename='debexpo/tests/changes/synce-hal_0.1-1_source.changes')

    def testInitialize(self):
        """
        Tests whether the two ways of creating a Changes object output the same result.
        """
        f = open('debexpo/tests/changes/synce-hal_0.1-1_source.changes')
        contents = f.read()
        f.close()

        a = Changes(filename='debexpo/tests/changes/synce-hal_0.1-1_source.changes')
        b = Changes(string=contents)

        self.assertEqual(a['Source'], b['Source'])

    def testGetitem(self):
        """
        Tests Changes.__getitem__.
        """
        self.assertEqual(self.changes['Source'], 'synce-hal')
        self.assertEqual(self.changes['Urgency'], 'low')

    def testGetFiles(self):
        """
        Tests Changes.get_files.
        """
        self.assertEqual(self.changes.get_files(), ['synce-hal_0.1-1.dsc', 'synce-hal_0.1.orig.tar.gz', 'synce-hal_0.1-1.diff.gz'])

    def testGetComponent(self):
        """
        Tests Changes.get_component().
        """
        self.assertEqual(self.changes.get_component(), 'main')

    def testGetPriority(self):
        """
        Tests Changes.get_priority().
        """
        self.assertEqual(self.changes.get_priority(), 'optional')

    def testGetDsc(self):
        """
        Tests Changes.get_dsc().
        """
        self.assertEqual(self.changes.get_dsc(), 'synce-hal_0.1-1.dsc')
