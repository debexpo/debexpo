#   test_closedbugs.py - Plugin ClosedBug test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste Beauplat <lyknode@cilg.org>
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
from debexpo.bugs.models import Bug, BugSeverity, BugType, BugStatus
from debexpo.plugins.models import PluginSeverity

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
        self.assert_plugin_result_count('hello', 'closed-bugs', 0)
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test package '
                                'for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_not_owned(self):
        self.import_source_package('hello-no-owned-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 9953)
        self.assertEquals(list(
            Bug.objects.get().sources.values_list('name', flat=True)),
            ['xloadimage'])

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.error)
        data = self.assert_plugin_result('hello', 'closed-bugs',
                                         'Package closes bugs in a wrong way')
        self.assertEquals(data['errors'],
                          ['Bug #9953 does not belong to this package'])
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test '
                                'package for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_rfs_bug(self):
        self.import_source_package('hello-close-rfs')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 815032)
        self.assertEquals(Bug.objects.get().bugtype, BugType.RFS)

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.error)
        data = self.assert_plugin_result('hello', 'closed-bugs',
                                         'Package closes bugs in a wrong way')
        self.assertEquals(data['errors'], ['Bug #815032 is a RFS bug'])
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 [RFS] -- Test '
                                'package for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_invalid_bugs(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()

        self.assertEquals(list(Bug.objects.all()), [])

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.error)
        data = self.assert_plugin_result('hello', 'closed-bugs',
                                         'Package closes bugs in a wrong way')
        self.assertEquals(data['errors'], ['Bug #0 does not exist'])
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test package '
                                'for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_multi_wnpp(self):
        self.import_source_package('hello-multi-wnpp')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get(number=637639).bugtype, BugType.ITA)
        self.assertEquals(Bug.objects.get(number=874387).bugtype, BugType.ITA)

        self.assert_plugin_severity('vnstat', 'closed-bugs',
                                    PluginSeverity.warning)
        self.assert_plugin_result(
            'vnstat', 'closed-bugs',
            'Package closes multiple wnpp bugs: ITA, ITA')
        self.assert_rfs_content('vnstat',
                                'Subject: RFS: vnstat/1.0-1 [ITA] -- Test '
                                'package for debexpo')
        self.assert_rfs_content('vnstat',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_closed_bugs(self):
        with self.settings(BUGS_REPORT_NOT_OPEN=True):
            self.import_source_package('hello-normal-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 906521)
        self.assertEquals(Bug.objects.get().status, BugStatus.done)

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.error)
        data = self.assert_plugin_result('hello', 'closed-bugs',
                                         'Package closes bugs in a wrong way')
        self.assertEquals(data['errors'],
                          ['Bug #906521 is closed'])
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test package '
                                'for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_normal_bug(self):
        self.import_source_package('hello-normal-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 906521)
        self.assertEquals(Bug.objects.get().severity, BugSeverity.normal)
        self.assertEquals(Bug.objects.get().bugtype, BugType.bug)
        self.assertEquals(Bug.objects.get().subject, 'Hello says `goodbye\'')
        Bug.objects.get(packages__name='hello')

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.info)
        self.assert_plugin_result('hello', 'closed-bugs',
                                  'Package closes bug')
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test package '
                                'for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_multi_bug(self):
        self.import_source_package('hello-multi-bug')
        self.assert_importer_succeeded()

        bugs = Bug.objects.all()
        self.assertEquals(len(bugs), 3)
        self.assertEquals(bugs[0].number, 616444)
        self.assertEquals(bugs[1].number, 696855)
        self.assertEquals(bugs[2].number, 719848)

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.info)
        self.assert_plugin_result('hello', 'closed-bugs',
                                  'Package closes bugs')
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test package '
                                'for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

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

        self.assert_plugin_severity('hello', 'closed-bugs',
                                    PluginSeverity.info)
        self.assert_plugin_result('hello', 'closed-bugs',
                                  'Package closes RC bug')
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 [RC] -- Test '
                                'package for debexpo')
        self.assert_rfs_content('hello',
                                'Severity: important')

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

        self.assert_plugin_severity('janest-ocaml-compiler-libs', 'closed-bugs',
                                    PluginSeverity.info)
        self.assert_plugin_result('janest-ocaml-compiler-libs', 'closed-bugs',
                                  'Package closes ITP bug')
        self.assert_rfs_content('janest-ocaml-compiler-libs',
                                'Subject: RFS: janest-ocaml-compiler-libs/1.0-1'
                                ' [ITP] -- Test package for debexpo')

    @unittest.skipIf(has_network, 'no network: {}'.format(has_network))
    def test_closes_ita_bug(self):
        self.import_source_package('hello-ita-bug')
        self.assert_importer_succeeded()

        self.assertEquals(Bug.objects.get().number, 931405)
        self.assertEquals(Bug.objects.get().severity, BugSeverity.normal)
        self.assertEquals(Bug.objects.get().bugtype, BugType.ITA)
        self.assertEquals(Bug.objects.get().subject,
                          'ITA: django-sortedm2m')

        self.assert_plugin_result_count('django-sortedm2m', 'closed-bugs', 1)
        self.assert_plugin_severity('django-sortedm2m', 'closed-bugs',
                                    PluginSeverity.info)
        self.assert_plugin_result('django-sortedm2m', 'closed-bugs',
                                  'Package closes ITA bug')
        self.assert_rfs_content('django-sortedm2m',
                                'Subject: RFS: django-sortedm2m/1.0-1 [ITA] --'
                                ' Test package for debexpo')
        self.assert_rfs_content('django-sortedm2m',
                                'Severity: normal')
