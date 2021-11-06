#   test_changes.py - unit testing for Changes
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2021 Baptiste Beauplat <lyknode@debian.org>
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
from os.path import join, dirname

from debexpo.tools.debian.changes import Changes

CHANGES_FILE_OK = join(dirname(__file__), '..', '..', '..', 'functional',
                       'importer', 'data', 'ok', 'hello_1.0-1_amd64.changes')


class TestChanges(TestController):
    def test_dsc_from_changes(self):
        changes = Changes(CHANGES_FILE_OK)
        changes.validate()
        changes.parse_dsc()

        source = changes.get_source()
        try:
            source.extract()
            source.parse_control_files()
        finally:
            source.remove()

        self.assertEquals(source, changes.get_source())
