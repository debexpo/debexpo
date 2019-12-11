#   test_subscriptions.py - Test the subscriptions list page
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

from django.urls import reverse

from tests import TestController
from debexpo.accounts.models import User
from debexpo.packages.models import Package
from debexpo.comments.models import PackageSubscription


class TestPackageController(TestController):
    def setUp(self):
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def test_bad_method_unsubscribe(self):
        self.client.post(reverse('login'), self._AUTHDATA)

        response = self.client.get(reverse(
            'unsubscribe_package', args=['testpackage']))
        self.assertEquals(response.status_code, 405)

    def test_no_auth_unsubscribe(self):
        response = self.client.post(reverse(
            'unsubscribe_package', args=['testpackage']))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_no_auth_subscriptions(self):
        response = self.client.post(reverse(
            'subscriptions'))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_subscriptions(self, package=None, create=False, delete=False,
                           comment=False, upload=False):
        sub = None

        # Create subscription if requested
        if create:
            user = User.objects.get(email='email@example.com')
            sub = PackageSubscription(package=package, on_comment=comment,
                                      on_upload=upload)
            sub.user = user
            sub.save()

        # Login and get subscriptions page
        self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.get(reverse('subscriptions'))

        # Assert page default content
        self.assertEquals(response.status_code, 200)
        self.assertIn('<h1>My subscription list</h1>', str(response.content))

        # Assert package subscription details
        if package:
            self.assertIn(package, str(response.content))

            if comment:
                self.assertIn('<li>comment</li>', str(response.content))

            if upload:
                self.assertIn('<li>upload</li>', str(response.content))

            if Package.objects.filter(name=package).exists():
                self.assertIn(reverse('package', args=[package]),
                              str(response.content))

        # Delete subscription if requested
        if delete:
            sub.delete()

        # Return the subscription, useful if not deleted
        return sub

    def test_edit_redirect_subscriptions(self):
        self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.post(reverse('subscribe_package',
                                    args=['testpackage']), {
            'package': 'package_name',
            'commit': 'submit',
        })

        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('subscriptions'), response.url)

    def test_new_redirect_subscriptions(self):
        self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.post(reverse('subscriptions'), {
            'package': 'package_name',
            'commit': 'submit',
        })

        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('subscribe_package', args=['package_name']),
                      response.url)

    def test_existing_package_subscriptions(self):
        self.test_subscriptions('testpackage', create=True, delete=True,
                                comment=False, upload=True)

    def test_non_existing_package_subscriptions(self):
        self.test_subscriptions('does_not_exists', create=True, delete=True,
                                comment=True, upload=True)

    def test_unsubscribe_subscriptions(self):
        sub = self.test_subscriptions('testpackage', create=True, delete=False,
                                      comment=False, upload=True)

        key = sub.id
        response = self.client.post(reverse('unsubscribe_package',
                                    args=['testpackage']))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('subscriptions'), response.url)
        self.assertRaises(PackageSubscription.DoesNotExist,
                          PackageSubscription.objects.get, pk=key)
