#   test_package.py - Test the package views
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

from django.core import mail
from django.urls import reverse
from django.test import override_settings
from django.conf import settings

from tests import TestController
from debexpo.accounts.models import User
from debexpo.packages.models import Package, PackageUpload, BinaryPackage
from debexpo.comments.models import PackageSubscription, UploadOutcome, Comment


class TestPackageController(TestController):
    def setUp(self):
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def _test_bad_method(self, action, args=None):
        if not args:
            args = []

        self.client.post(reverse('login'), self._AUTHDATA)

        response = self.client.get(reverse(
            action, args=['testpackage'] + args))
        self.assertEquals(response.status_code, 405)

    def _test_no_auth(self, action, redirect_login=True, args=None):
        if not args:
            args = []

        response = self.client.post(reverse(
            action, args=['testpackage'] + args))
        self.assertEquals(response.status_code, 302)

        if (redirect_login):
            self.assertIn(reverse('login'), response.url)

    def _test_not_owned_package(self, action, method='get', args=None):
        if not args:
            args = []

        user = User.objects.create_user(name='Another user',
                                        email='another@example.com',
                                        password='password')
        user.save()

        self.client.post(reverse('login'), {'username': 'another@example.com',
                                            'password': 'password',
                                            'commit': 'submit'})

        response = self.client.post(reverse(action,
                                            args=['testpackage'] + args))
        self.assertEquals(response.status_code, 403)
        user.delete()

    def test_index(self):
        # No package redirects to package list
        response = self.client.get(reverse('package_index'))
        self.assertEquals(response.status_code, 301)
        self.assertEquals(reverse('packages'), response.url)

        # Wrong package produce 404
        response = self.client.get(reverse('package', args=['notapackage']))
        self.assertEquals(response.status_code, 404)

        # Write package show details
        # Unauthenticated
        response = self.client.get(reverse('package', args=['testpackage']))
        self.assertEquals(response.status_code, 200)

        self.assertIn(reverse('packages_search',
                              args=['uploader', 'email@example.com']),
                      str(response.content))

        # And authenticated
        response = self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.get(reverse('package', args=['testpackage']))
        self.assertEquals(response.status_code, 200)

        self.assertIn(reverse('delete_package',
                              args=['testpackage']),
                      str(response.content))
        self.assertIn(reverse('comment_package',
                              args=['testpackage']),
                      str(response.content))

        # Without description
        package = Package.objects.get(name='testpackage')
        upload = PackageUpload.objects.get(package=package)
        binary = BinaryPackage.objects.get(upload=upload)
        binary.delete()

        response = self.client.get(reverse('package', args=['testpackage']))
        self.assertEquals(response.status_code, 200)

        self.assertNotIn('A short description here',
                         str(response.content))

    def test_subscribe(self):
        # Not authenticated
        response = self.client.get(reverse('subscribe_package',
                                           args=['testpackage']))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Authenticated
        # Get subscription page
        self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.get(reverse('subscribe_package',
                                           args=['testpackage']))

        self.assertEquals(response.status_code, 200)

        # Post to update subscription
        self._subscribe('testpackage', True, False)
        self._subscribe('testpackage', False, True)
        self._subscribe('testpackage', False, False)

    def _subscribe(self, package, on_upload, on_comment):
        response = self.client.post(reverse('subscribe_package',
                                            args=[package]), {
            'on_upload': on_upload,
            'on_comment': on_comment,
            'next': package,
            'commit': 'submit'
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(reverse('package', args=[package]),
                          response.url)
        if not (on_upload or on_comment):
            self.assertRaises(PackageSubscription.DoesNotExist,
                              PackageSubscription.objects.get, package=package)
        else:
            subs = PackageSubscription.objects.get(package=package)
            self.assertEquals(subs.on_upload, on_upload)
            self.assertEquals(subs.on_comment, on_comment)

    def test_delete_no_auth(self):
        self._test_no_auth('delete_package')
        self._test_no_auth('delete_upload', args=['1'])

    def test_delete_not_owned_package(self):
        self._test_not_owned_package('delete_package')
        self._test_not_owned_package('delete_upload', args=['1'])

    def test_delete_bad_method(self):
        self._test_bad_method('delete_package')
        self._test_bad_method('delete_upload', args=['1'])

#    def test_delete_gitstorage_utf8(self):
#        gitdir = join(pylons.test.pylonsapp.config['debexpo.repository'],
#                      'git', 'testpackage', 'source')
#
#        makedirs(gitdir)
#        with open(join(gitdir, 'Bodø'), 'w'):
#            pass
#
#        self.test_delete_successful()

    def test_delete_successful(self):
        self.client.post(reverse('login'), self._AUTHDATA)

        response = self.client.post(reverse(
            'delete_package', args=['testpackage']))

        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('packages_my'), response.url)
        self.assertRaises(Package.DoesNotExist, Package.objects.get,
                          name='testpackage')

    @override_settings()
    def test_delete_successful_no_gitstorage(self):
        del settings.GIT_STORAGE

        self.test_delete_successful()

    @override_settings()
    def test_delete_upload_successful_no_gitstorage(self):
        del settings.GIT_STORAGE

        self.client.post(reverse('login'), self._AUTHDATA)

        response = self.client.post(reverse(
            'delete_upload', args=['testpackage', '1']))

        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('packages_my'), response.url)
        self.assertRaises(Package.DoesNotExist, Package.objects.get,
                          name='testpackage')

    def test_delete_single_upload_successful(self):
        self._setup_example_package()
        self.client.post(reverse('login'), self._AUTHDATA)

        response = self.client.post(reverse(
            'delete_upload', args=['testpackage', '1']))

        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('package', args=['testpackage']), response.url)
        Package.objects.get(name='testpackage')

    def test_comment_no_auth(self):
        self._test_no_auth('comment_package')

    def test_comment_bad_method(self):
        self._test_bad_method('comment_package')

    def test_comment_bad_form(self):
        self.client.post(reverse('login'), self._AUTHDATA)

        upload = PackageUpload.objects.filter(package__name='testpackage') \
            .earliest('uploaded')
        response = self.client.post(reverse('comment_package',
                                            args=['testpackage']), {
            'upload_id': upload.id,
            'text': 'This is a test comment',
            'outcome': 42,
            'commit': 'submit_comment'
        })

        self.assertEquals(response.status_code, 200)
        self.assertIn('errorlist', str(response.content))

    def test_comment(self):
        self.client.post(reverse('login'), self._AUTHDATA)

        upload = PackageUpload.objects.filter(package__name='testpackage') \
            .earliest('uploaded')
        response = self.client.post(reverse('comment_package',
                                            args=['testpackage']), {
            'upload_id': upload.id,
            'text': 'This is a test comment',
            'outcome': UploadOutcome.needs_work.value,
            'commit': 'submit_comment'
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            f"{reverse('package', args=['testpackage'])}#upload-1",
            response.url)

        comment = Comment.objects.get(upload=upload)

        self.assertEquals(comment.text, 'This is a test comment')
        self.assertFalse(comment.uploaded)

        response = self.client.get(reverse('package', args=['testpackage']))
        self.assertEquals(response.status_code, 200)

        self.assertIn('This is a test comment', str(response.content))
        self.assertIn('Needs work', str(response.content))

        comment.delete()

    def test_comment_with_subscriber(self):
        # test with a subscriber
        self.client.post(reverse('login'), self._AUTHDATA)

        user = User.objects.get(email='email@example.com')
        packsub = PackageSubscription(
            package='testpackage',
            on_comment=True,
            on_upload=False,
        )
        packsub.user = user
        packsub.save()

        self.test_comment()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('This is a test comment', mail.outbox[0].body)
        self.assertIn('From: debexpo <no-reply@example.org>',
                      str(mail.outbox[0].message()))

    def test_sponsor_no_auth(self):
        self._test_no_auth('sponsor_package')

    def test_sponsor_not_owned_package(self):
        self._test_not_owned_package('sponsor_package')

    def test_sponsor_bad_method(self):
        self._test_bad_method('sponsor_package')

    def test_sponsor_toggle(self, toggle=True):
        self.client.post(reverse('login'), self._AUTHDATA)

        response = self.client.post(reverse(
            'sponsor_package', args=['testpackage']))

        self.assertEquals(response.status_code, 302)

        package = Package.objects.get(name='testpackage')

        if (toggle):
            self.assertTrue(package.needs_sponsor)
            self.test_sponsor_toggle(toggle=False)
        else:
            self.assertFalse(package.needs_sponsor)

#    def test_package_info(self, data=False):
#        package = Package.objects.get(name='testpackage')
#        upload = PackageUpload.objects.filter(package__name='testpackage') \
#            .latest('uploaded')
#        textmark = 'some lintian output'
#
#        if data:
#            package_info_data = PackageInfo(
#                package_version_id=package_version.id,
#                from_plugin='LintianPlugin',
#                outcome='Package is lintian clean',
#                data=textmark,
#                severity=constants.PLUGIN_SEVERITY_INFO)
#        else:
#            package_info_data = PackageInfo(
#                package_version_id=package_version.id,
#                from_plugin='LintianPlugin',
#                outcome='Package is lintian clean',
#                rich_data=textmark,
#                severity=constants.PLUGIN_SEVERITY_INFO)
#
#        package_info_data.save()
#
#        response = self.client.get(reverse('package', args=['testpackage']))
#
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue(textmark in response)

#    def test_package_info_data(self):
#        self.test_package_info(data=True)
