#   test_closedbugs.py - Plugin ClosedBug test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from tests.functional.importer import TestImporterController, test_network
# from debexpo.lib.constants import PLUGIN_SEVERITY_INFO, PLUGIN_SEVERITY_ERROR
from debexpo.bugs.models import Bug, BugSeverity, BugType

import unittest

has_network = test_network()


class TestPluginClosedBug(TestImporterController):
    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_bug_multi_package(self):
        Bug.objects.fetch_bugs([947936])
        Bug.objects.get(packages__name='chrony')
        Bug.objects.get(packages__name='systemd')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_no_bugs(self):
        self.import_source_package('hello-no-bug')
        self.assert_importer_succeeded()

        self.assertEquals(list(Bug.objects.all()), [])

        # self.assert_package_no_info('hello', 'closedbugs')
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 -- Test package '
        #                         'for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_invalid_bugs(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()

        self.assertEquals(list(Bug.objects.all()), [])

        # self.assert_package_severity('hello', 'closedbugs',
        #                              PLUGIN_SEVERITY_ERROR)
        # self.assert_package_info('hello', 'closedbugs',
        #                          'Package closes bugs in a wrong way')
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 -- Test package '
        #                         'for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_normal_bug(self):
        self.import_source_package('hello-normal-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 906521)
        self.assertEquals(Bug.objects.get().severity, BugSeverity.normal)
        self.assertEquals(Bug.objects.get().bugtype, BugType.bug)
        self.assertEquals(Bug.objects.get().subject, 'Hello says `goodbye\'')
        Bug.objects.get(packages__name='hello')

        # self.assert_package_severity('hello', 'closedbugs',
        #                              PLUGIN_SEVERITY_INFO)
        # self.assert_package_info('hello', 'closedbugs',
        #                          'Package closes bug')
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 -- Test package '
        #                         'for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_multi_bug(self):
        self.import_source_package('hello-multi-bug')
        self.assert_importer_succeeded()

        bugs = Bug.objects.all()
        self.assertEquals(len(bugs), 3)
        self.assertEquals(bugs[0].number, 616444)
        self.assertEquals(bugs[1].number, 696855)
        self.assertEquals(bugs[2].number, 719848)

        # self.assert_package_severity('hello', 'closedbugs',
        #                              PLUGIN_SEVERITY_INFO)
        # self.assert_package_info('hello', 'closedbugs',
        #                          'Package closes bugs')
        # for bug in ('616444', '696855', '719848'):
        #     self.assert_package_data('hello', 'closedbugs',
        #                              bug)
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 -- Test package '
        #                         'for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_rc_bug(self):
        self.import_source_package('hello-rc-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 928887)
        self.assertEquals(Bug.objects.get().severity, BugSeverity.serious)
        self.assertEquals(Bug.objects.get().bugtype, BugType.bug)
        self.assertEquals(Bug.objects.get().subject,
                          'hello: version skew: 2.10-1+deb9u1 '
                          '(stretch-security) > 2.10-1 (buster)')

        # self.assert_package_severity('hello', 'closedbugs',
        #                              PLUGIN_SEVERITY_INFO)
        # self.assert_package_info('hello', 'closedbugs',
        #                          'Package closes a RC bug')
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 [RC] -- Test '
        #                         'package for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: important')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_itp_bug(self):
        self.import_source_package('hello-itp-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 934896)
        self.assertEquals(Bug.objects.get().severity, BugSeverity.wishlist)
        self.assertEquals(Bug.objects.get().bugtype, BugType.ITP)
        self.assertEquals(Bug.objects.get().subject,
                          'ITP: janest-ocaml-compiler-libs -- OCaml compiler'
                          ' libraries repackaged')

        # self.assert_package_severity('hello', 'closedbugs',
        #                              PLUGIN_SEVERITY_INFO)
        # self.assert_package_info('hello', 'closedbugs',
        #                          'Package closes a ITP bug')
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 [ITP] -- Test '
        #                         'package for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: wishlist')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_ita_bug(self):
        self.import_source_package('hello-ita-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 931405)
        self.assertEquals(Bug.objects.get().severity, BugSeverity.normal)
        self.assertEquals(Bug.objects.get().bugtype, BugType.ITA)
        self.assertEquals(Bug.objects.get().subject,
                          'ITA: django-sortedm2m')

        # self.assert_package_severity('hello', 'closedbugs',
        #                              PLUGIN_SEVERITY_INFO)
        # self.assert_package_info('hello', 'closedbugs',
        #                          'Package closes a ITA bug')
        # self.assert_rfs_content('hello',
        #                         'Subject: RFS: hello/1.0-1 [ITA] -- Test '
        #                         'package for debexpo')
        # self.assert_rfs_content('hello',
        #                         'Severity: normal')
