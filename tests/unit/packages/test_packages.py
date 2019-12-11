#   test_packages.py - unit tests for packages views
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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
from debexpo.packages.models import Package, Priority, Project, Distribution, \
    Section, Component, BinaryPackage


class TestPackagesController(TestController):
    def setUp(self):
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def test_str_representation(self):
        testing_set = (
            (Project.objects.get, 'Debian'),
            (Distribution.objects.get, 'buster'),
            (Component.objects.get, 'non-free'),
            (Section.objects.get, 'admin'),
            (Priority.objects.get, 'optional'),
            (Package.objects.get, 'testpackage'),
        )

        for fetch, item_name in testing_set:
            self.assertEquals(str(fetch(name=item_name)), item_name)

    def test_get_description(self):
        package = Package.objects.get(name='testpackage')

        self.assertEquals('A short description here', package.get_description())

        binary = BinaryPackage.objects.get(upload__package__name='testpackage')
        binary.delete()

        self.assertEquals('', package.get_description())
