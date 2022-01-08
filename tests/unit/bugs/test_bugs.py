#   test_bugs.py - Test debexpo Bug model
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2022 Baptiste Beauplat <lyknode@debian.org>
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

from tests import TestController

from debexpo.bugs.models import Bug


class TestBugs(TestController):
    def test_guess_packages(self):
        # Normal bug
        packages = Bug.objects._guess_packages(
            'package1',
            'FTBFS: with foo from experimental'
        )

        self.assertEquals(len(packages), 1)
        self.assertEquals(packages[0].name, 'package1')

        # Bug linked to multiple packages
        packages = Bug.objects._guess_packages(
            'package1,package2',
            'FTBFS: with foo from experimental'
        )

        self.assertEquals(len(packages), 2)
        self.assertEquals(packages[0].name, 'package1')
        self.assertEquals(packages[1].name, 'package2')

        # WNPP/sponsorship-requests
        packages = Bug.objects._guess_packages(
            'wnpp',
            'ITP: foo -- A stable and useful software'
        )

        self.assertEquals(len(packages), 1)
        self.assertEquals(packages[0].name, 'foo')

        # WNPP/sponsorship-requests, wrong subject
        packages = Bug.objects._guess_packages(
            'wnpp',
            'wait, there is a format for the subject?'
        )

        self.assertEquals(len(packages), 0)
