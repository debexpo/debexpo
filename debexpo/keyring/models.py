#   models.py - models for keyring app
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

from django.db import models
from django.utils.translation import gettext_lazy as _

from debexpo.accounts.models import User


class GPGAlgo(models.Model):
    name = models.TextField(max_length=10, verbose_name=_('Type'))
    gpg_algorithm_id = models.PositiveSmallIntegerField(
        verbose_name=_('GPG Algorithm ID')
    )
    minimal_size_requirement = models.PositiveSmallIntegerField(
        verbose_name=_('Minimal size requirment'), blank=True, null=True
    )

    def __str__(self):
        return self.name


class Key(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.TextField(verbose_name=_('OpenGPG key'))
    fingerprint = models.TextField(max_length=40, verbose_name=_('Fingerprint'))
    last_updated = models.DateTimeField(verbose_name=_('Last update on'),
                                        auto_now=True)

    # We store here the algorithm and the size to avoid creating a
    # VirtualKeyring to get those information each time a user loads its
    # profile.
    algorithm = models.ForeignKey(GPGAlgo, on_delete=models.SET_NULL,
                                  blank=True, null=True,
                                  verbose_name=_('Type'))
    size = models.PositiveSmallIntegerField(verbose_name=_('Size'))
