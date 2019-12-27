#   models.py - models for comments
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

from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _, activate, get_language
from django.urls import reverse

from debexpo.accounts.models import User
from debexpo.packages.models import PackageUpload, Package
from debexpo.tools.email import Email


class UploadOutcome(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    unreviewed = (1, _('Not reviewed'))
    needs_work = (2, _('Needs work'))
    ready = (3, _('Ready'))

    @classmethod
    def as_tuple(cls):
        return (cls.unreviewed.tuple,
                cls.needs_work.tuple,
                cls.ready.tuple,)


class PackageSubscriptionManager(models.Manager):
    def get_recipients(self, package, event):
        return PackageSubscription.objects.filter(**{
            'package': package,
            f'on_{event}': True,
        }).values_list('user__email', flat=True)


class PackageSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.CharField(max_length=100, verbose_name=_('Name'))

    on_upload = models.BooleanField(verbose_name=_('Subscribe to uploads'))
    on_comment = models.BooleanField(verbose_name=_('Subscribe to comments'))

    objects = PackageSubscriptionManager()

    class Meta:
        unique_together = ('user', 'package',)

    def get_subscriptions(self):
        subscriptions = []

        for event in ('upload', 'comment'):
            if getattr(self, f'on_{event}'):
                subscriptions.append(event)

        return subscriptions

    def can_delete(self):
        return not bool(self.get_subscriptions())

    def package_exists(self):
        return Package.objects.filter(name=self.package).exists()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upload = models.ForeignKey(PackageUpload, on_delete=models.CASCADE)

    text = models.TextField(verbose_name=_('Comment'))
    date = models.DateTimeField(verbose_name=_('Comment date'),
                                auto_now_add=True)

    outcome = models.PositiveSmallIntegerField(
        verbose_name=_('Upload outcome'), choices=UploadOutcome.as_tuple()
    )
    uploaded = models.BooleanField(verbose_name=_('Uploaded to debian'))

    def notify(self, request):
        package = self.upload.package.name
        uploader = self.upload.uploader.email
        commenter = self.user.email
        lang = get_language()

        # Get subscription list for our package
        recipients = set(PackageSubscription.objects.get_recipients(
            package, 'upload'))

        # Remove commenter and uploader
        recipients -= set([commenter, uploader])

        # Send notification (always in english as i18n only is available on
        # requests)
        email = Email('email-comment.html')
        activate('en')
        email.send(
            _('New comment on package {}').format(package),
            recipients,
            comment=self,
            package_url=request.build_absolute_uri(
                reverse('package', args=[package])),
            subscription_url=request.build_absolute_uri(
                reverse('subscriptions')),
        )

        # For the uploader
        email.send(
            _('New comment on package {}').format(package),
            [uploader],
            comment=self,
            package_url=request.build_absolute_uri(
                reverse('package', args=[package])),
            subscription_url=request.build_absolute_uri(
                reverse('subscriptions')),
        )

        # Restore language context
        activate(lang)

    def get_outcome(self):
        return UploadOutcome(self.outcome)
