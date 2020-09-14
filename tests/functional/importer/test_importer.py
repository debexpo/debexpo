#   test_upload.py — UploadController test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2018-2020 Baptiste Beauplat <lyknode@cilg.org>
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
UploadController test cases.
"""

# from os import makedirs
from os.path import join
from os import utime, unlink
from time import time

from django.conf import settings
from django.core import mail
from django.test import override_settings

from tests.functional.importer import TestImporterController
from tests.functional.importer.source_package import TestSourcePackage

from debexpo.importer.models import Importer, ExceptionImporterRejected


class TestImporter(TestImporterController):
    """
    This class tests debexpo's importer.

    Its goal is to process a user upload, validate it and reject it with a email
    sent to the user or accepting it and making it available in debexpo repo
    """

    _ORPHAN_GPG_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW/F8GBYJKwYBBAHaRw8BAQdA6Riq9GZh/HiwtFjPcvz5i5oFzp1I8RiqxBs1
g06oSh+0HXByaW1hcnkgaWQgPG1haW5AZXhhbXBsZS5vcmc+iJMEExYIADsCGwMF
CwkIBwIGFQoJCAsCBBYCAwECHgECF4AWIQSGVz4uSUdVmCPsPxTH4ZqYGuqOuwUC
W/F8dAIZAQAKCRDH4ZqYGuqOu9GTAQCCMRbXuueDLcC4eWmMGGiAmqLzKdhGJxQe
e0k5d6wkKQEA2vdlMg9s3UFL4e8jnJPYeNpsxDaaEPr0jMLnwcBp8wa0JWRlYmV4
cG8gdGVzdGluZyA8ZGViZXhwb0BleGFtcGxlLm9yZz6IkAQTFggAOBYhBIZXPi5J
R1WYI+w/FMfhmpga6o67BQJb8XxSAhsDBQsJCAcCBhUKCQgLAgQWAgMBAh4BAheA
AAoJEMfhmpga6o67MjUBAMYVSthPo3oKR1PpV9ebHFiSARmc2BxxL+xmdzfiRT3O
AP9JQZxCSl3awI5xos8mw2edsDWYcaS2y+RmbTLv8wR2Abg4BFvxfBgSCisGAQQB
l1UBBQEBB0Doc/H7Tyvf+6kdlnUOqY+0t3pkKYj0EOK6QFKMnlRpJwMBCAeIeAQY
FggAIBYhBIZXPi5JR1WYI+w/FMfhmpga6o67BQJb8XwYAhsMAAoJEMfhmpga6o67
Vh8A/AxTKLqACJnSVFrO2sArc7Yt3tymB+of9JeBF6iYBbuDAP9r32J6TYFB9OSz
r1JREXlgQRuRdd5ZWSvIxKaKGVbYCw==
=BMLr
-----END PGP PUBLIC KEY BLOCK-----
"""

    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_import_package_empty_changes(self):
        self.import_package('emtpy-changes')
        self.assert_importer_succeeded()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_corrupted_changes(self):
        self.import_package('corrupted-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_missing_file_in_changes(self):
        self.import_package('missing-file-in-changes')
        self.assert_importer_failed()
        self.assert_email_with('hello_1.0-1.debian.tar.xz is missing from'
                               ' upload')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_wrong_checksum_in_changes(self):
        self.import_package('wrong-checksum-in-changes')
        self.assert_importer_failed()
        self.assert_email_with('Checksum failed for file hello_1.0-1.dsc')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_no_dsc(self):
        self.import_package('no-dsc')
        self.assert_importer_failed()
        self.assert_email_with('dsc is missing from changes')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_dsc_corrupted(self):
        self.import_package('corrupted-dsc')
        self.assert_importer_failed()
        self.assert_email_with('could not be parsed')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_dsc_missing_key(self):
        self.import_package('missing-key-in-dsc')
        self.assert_importer_failed()
        self.assert_email_with('Missing key Version')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_corrupted_source(self):
        self.import_package('corrupted-source')
        self.assert_importer_failed()
        self.assert_email_with('Failed to extract source package')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_corrupted_changlog(self):
        self.import_package('corrupted-changelog')
        self.assert_importer_failed()
        self.assert_email_with('Could not parse changelog')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_no_dep5_copyright(self):
        self.import_source_package('hello-license-no-dep5')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')

    def test_import_package_invalid_copyright(self):
        self.import_source_package('hello-license-invalid')
        self.assert_importer_failed()
        self.assert_email_with('Files paragraph missing License field')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_invalid2_copyright(self):
        self.import_source_package('hello-license-invalid2')
        self.assert_importer_failed()
        self.assert_email_with('continued line must begin with " "')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def _import_package_bad_encoding_source(self, filename):
        self.import_source_package(f'hello-bad-encoding-{filename}')
        self.assert_importer_failed()
        self.assert_email_with("'utf-8' codec can't decode byte")
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_bad_encoding(self):
        for filename in ('control', 'copyright', 'changelog',):
            self._import_package_bad_encoding_source(filename)
            self._cleanup_mailbox()

    def test_import_package_control_no_source(self):
        self.import_package('control-no-source')
        self.assert_importer_failed()
        self.assert_email_with('No source definition found')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_control_no_binary(self):
        self.import_package('control-no-binary')
        self.assert_importer_failed()
        self.assert_email_with('No binary definition found')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_control_missing_key_source(self):
        self.import_package('control-missing-key-source')
        self.assert_importer_failed()
        self.assert_email_with('Missing key Maintainer')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_control_missing_key_binary(self):
        self.import_package('control-missing-key-binary')
        self.assert_importer_failed()
        self.assert_email_with('Missing key Architecture')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_not_signed(self):
        self.import_package('not-signed')
        self.assert_importer_failed()
        self.assert_email_with('not a GPG signed file')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_unknown_key(self):
        self.import_package('unknown-key')
        self.assert_importer_failed()
        self.assert_email_with('No public key found for key')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_no_email(self):
        self.import_source_package('hello', skip_email=True)
        self.assert_importer_succeeded()
        self.assert_no_email()

    # def test_import_package_wrong_gpg_uid(self):
    #     self._add_gpg_key(self._ORPHAN_GPG_KEY)
    #     self.import_package('wrong-gpg-uid')
    #     self.assert_importer_failed()
    #     self.assert_email_with('Your GPG key does not match the email used to'
    #                            ' register')
    #     self.assert_package_count('hello', '1.0-1', 0)
    #     self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_invalid_dist(self):
        self.import_source_package('invalid-dist')
        self.assert_importer_failed()
        self.assert_email_with('Distribution trusty is not supported on '
                               'mentors')
        self.assert_email_with('List of supported distributions')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_no_orig(self):
        self.import_package('no-orig')
        self.assert_importer_failed()
        self.assert_email_with('error: missing orig.tar or debian.tar file in'
                               ' v2.0 source package')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_debian_orig_too_big(self):
        self.import_package('debian-orig-too-big')
        self.assert_importer_failed()
        self.assert_email_with('The original tarball cannot be retrieved from'
                               ' Debian: file too big (> 100MB)')
        self.assert_package_count('0ad-data', '0.0.23.1-1.1', 0)
        self.assert_package_not_in_repo('0ad-data', '0.0.23.1-1.1')

    def test_import_package_mismatch_orig_official(self):
        self.import_source_package('mismatch-orig')
        self.assert_importer_failed()
        self.assert_email_with('Source package origin file differs from the '
                               'official archive')
        self.assert_package_count('0ad-data', '0.0.23.1-2', 0)
        self.assert_package_not_in_repo('0ad-data', '0.0.23.1-2')

    def test_import_package_hello_unicode(self):
        self.import_source_package('unicode-changes')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')
        # self.assert_plugin_result('hello', 'debianqa',
        #                          'Package is already in Debian')

    # def test_import_package_hello_no_repository(self):
    #     repo = pylonsapp.config.pop('debexpo.repository')
    #     self.import_source_package('hello')
    #     pylonsapp.config['debexpo.repository'] = repo
    #     self.assert_importer_failed()
    #     self.assert_email_with("There was a failure in importing your "
    #                            "package")
    #     self.assert_package_count('hello', '1.0-1', 0)
    #     self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_hello_missing_orig(self):
        self.import_source_package('hello-mismatch-orig')
        self.assert_importer_failed()
        self.assert_email_with("hello_1.0.orig.tar.xz is missing from "
                               "upload")
        self.assert_package_count('hello', '1.0-2', 0)
        self.assert_package_not_in_repo('hello', '1.0-2')

    def test_import_package_not_in_debian(self):
        self.import_source_package('not-in-debian')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package "
                               "'this-package-should-not-exist' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('this-package-should-not-exist', '1.0-1', 1)
        self.assert_package_in_repo('this-package-should-not-exist', '1.0-1')
    #     self.assert_package_info('this-package-should-not-exist', 'debianqa',
    #                              'Package is not in Debian')

    # def test_import_package_hello_with_subscribers(self):
    #     self.setup_subscribers('hello')
    #     self.import_source_package('hello')
    #     self.assert_importer_succeeded()
    #     self.assert_email_with('hello 1.0-1 has been uploaded to the archive')
    #     self.assert_package_count('hello', '1.0-1', 1)
    #     self.assert_package_in_repo('hello', '1.0-1')

    # def test_import_package_hello_inconsistent_gitstorage(self):
    #     makedirs(join(pylonsapp.config['debexpo.repository'], 'git', 'hello'))
    #     self.import_source_package('hello')
    #     self.assert_importer_succeeded()
    #     self.assert_email_with("Your upload of the package 'hello' to "
    #                            + settings.SITE_NAME
    #                            + " was\nsuccessful.")
    #     self.assert_package_count('hello', '1.0-1', 1)
    #     self.assert_package_in_repo('hello', '1.0-1')

    # def test_import_package_hello_reject_dist(self):
    #     self.import_source_package('hello')
    #     self.assert_importer_succeeded()
    #     self.assert_email_with("Your upload of the package 'hello' to "
    #                            + settings.SITE_NAME
    #                            + " was\nsuccessful.")
    #     self.assert_package_count('hello', '1.0-1', 1)
    #     self.assert_package_in_repo('hello', '1.0-1')

    #     self._cleanup_mailbox()
    #     self.import_source_package('hello-other-dist')
    #     self.assert_importer_failed()
    #     self.assert_email_with('An upload with the same version but '
    #                            'different distribution exists on mentors.')
    #     self.assert_package_count('hello', '1.0-1', 1)
    #     self.assert_package_in_repo('hello', '1.0-1')

    def test_import_recursive_pool(self):
        self.import_source_package('hello', sub_dir='sub')
        self.assert_importer_succeeded()
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')

    def test_import_no_network_access(self):
        with self.settings(DEBIAN_ARCHIVE_URL='http://no-nxdomain',
                           TRACKER_URL='http://no-nxdomain',
                           FTP_MASTER_NEW_PACKAGES_URL='http://no-nxdomain',
                           FTP_MASTER_API_URL='http://no-nxdomain'):
            self.import_source_package('hello', sub_dir='sub')
        self.assert_importer_succeeded()
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')

    @override_settings()
    def test_import_package_hello(self):
        del settings.GIT_STORAGE

        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')
        # self.assert_plugin_data('hello', 'debianqa', '{"latest-upload": "')

        # Test email urls:
        self.assert_email_with(f'{settings.SITE_URL}/package/hello')
        self.assert_email_with(f'{settings.SITE_URL}/debian/pool/main/h/hello/'
                               'hello_1.0-1.dsc')
        self.assert_email_with(f'{settings.SITE_URL}/sponsors/rfs-howto/hello')

        self._cleanup_mailbox()
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 2)
        self.assert_package_in_repo('hello', '1.0-1')

        self.remove_package('hello', '1.0-1')
        self._assert_no_leftover(str(join(self.repository, 'pool')))

    def test_import_package_htop_download_orig(self):
        self.import_package('orig-from-official')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'htop' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('htop', '2.2.0-1', 1)
        self.assert_package_in_repo('htop', '2.2.0-1')
        for filename in ('htop_2.2.0-1.dsc',
                         'htop_2.2.0-1.debian.tar.xz',
                         'htop_2.2.0.orig.tar.gz',
                         'htop_2.2.0.orig.tar.gz.asc'):
            self.assert_file_in_repo(filename)

        self._cleanup_mailbox()
        self.import_package('orig-from-official')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'htop' to "
                               + settings.SITE_NAME
                               + " was\nsuccessful.")
        self.assert_package_count('htop', '2.2.0-1', 2)
        self.assert_package_in_repo('htop', '2.2.0-1')
        for filename in ('htop_2.2.0-1.dsc',
                         'htop_2.2.0-1.debian.tar.xz',
                         'htop_2.2.0.orig.tar.gz',
                         'htop_2.2.0.orig.tar.gz.asc'):
            self.assert_file_in_repo(filename)

        self.remove_package('htop', '2.2.0-1')
        self._assert_no_leftover(str(join(self.repository, 'pool')))

    # Since we cannot really make the importer fail (it is not supposed to
    # happend), we test that the field method can report an error to admins and
    # optionnaly to uploader if available.
    def test_importer_reject_no_maintainer(self):
        source_package = TestSourcePackage('hello-bad-changes-email')

        source_package.build()
        self._upload_package(join(self.data_dir,
                                  source_package.get_package_dir()))

        importer = Importer(str(self.spool))
        changes = self.spool.changes_to_process()[0]

        importer._reject(ExceptionImporterRejected(
            changes, 'Package rejected',
            ValueError('Some error'))
        )
        changes.remove()

        self.assertEquals(len(mail.outbox), 0)

    def test_importer_fail_no_maintainer(self):
        self._upload_package(join(self.data_dir, 'changes-no-maintainer'))

        importer = Importer(str(self.spool))
        changes = self.spool.changes_to_process()[0]

        importer._fail(ExceptionImporterRejected(
            changes, 'Importer failed',
            IOError('No space left on device'))
        )
        changes.remove()

        self.assertEquals(len(mail.outbox), 1)
        self.assertIn('No space left', mail.outbox[0].body)
        self.assertIn(settings.DEFAULT_FROM_EMAIL, mail.outbox[0].to)

    def test_importer_fail_with_maintainer(self):
        self._upload_package(join(self.data_dir, 'not-signed'))

        importer = Importer(str(self.spool))
        changes = self.spool.changes_to_process()[0]

        importer._fail(ExceptionImporterRejected(
            changes, 'Importer failed',
            IOError('No space left on device'))
        )
        changes.remove()

        self.assertEquals(len(mail.outbox), 1)
        self.assertIn('No space left', mail.outbox[0].body)
        self.assertIn(settings.DEFAULT_FROM_EMAIL, mail.outbox[0].to)
        self.assertIn(changes.uploader, mail.outbox[0].to)

    def test_importer_cleanup(self):
        deb = join(self.spool.get_queue_dir('incoming'), 'file.deb')
        deb_expired = join(self.spool.get_queue_dir('incoming'), 'old.deb')
        txt = join(self.spool.get_queue_dir('incoming'), 'file.txt')
        expired = time() - 6 * 60 * 60 - 1

        for path in (deb, deb_expired, txt,):
            with open(path, 'w'):
                pass

        utime(deb_expired, (expired, expired))

        importer = Importer(str(self.spool))
        importer.process_spool()

        unlink(deb)
