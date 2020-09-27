#   models.py - models for keyring app
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

from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from debexpo.accounts.models import User
from debexpo.tools.gnupg import GnuPG, ExceptionGnuPG, \
    ExceptionGnuPGMultipleKeys

import logging
log = logging.getLogger(__name__)


class GPGAlgo(models.Model):
    name = models.TextField(max_length=10, verbose_name=_('Type'))
    gpg_algorithm_id = models.PositiveSmallIntegerField(
        verbose_name=_('GPG Algorithm ID')
    )
    minimal_size_requirement = models.PositiveSmallIntegerField(
        verbose_name=_('Minimal size requirment'), null=True
    )

    def __str__(self):
        return self.name


class KeyManager(models.Manager):
    def import_key(self, data):
        gpg = GnuPG()

        gpg.import_key(data)
        keyring = gpg.get_keys_data()

        if (len(keyring) > 1):
            raise ExceptionGnuPGMultipleKeys(_('Multiple keys not supported'))

        return keyring[0]

    def _validate_algorithm(self, key):
        algorithm_id = key.get_algo()

        try:
            algorithm = GPGAlgo.objects.get(gpg_algorithm_id=algorithm_id)
        except GPGAlgo.DoesNotExist:
            raise ExceptionGnuPG(_(
                'Key algorithm not supported. Key must be one of the'
                ' following: {}'
            ).format(', '.join(map(str, GPGAlgo.objects.all()))))

        return algorithm

    def _validate_size(self, key, algorithm):
        size = int(key.get_size())
        min_size = algorithm.minimal_size_requirement
        if min_size and size < min_size:
            raise ExceptionGnuPG(_('Key size too small. Need at least'
                                   ' {} bits.').format(min_size))

        return size

    def get_key_by_fingerprint(self, fingerprint):
        return self.filter(Q(fingerprint=fingerprint) |
                           Q(subkey__fingerprint=fingerprint) |
                           Q(fingerprint__endswith=fingerprint) |
                           Q(subkey__fingerprint__endswith=fingerprint)) \
                                .distinct().get()

    def parse_key_data(self, data):
        key = self.import_key(data)

        user_key = Key()
        user_key.algorithm = self._validate_algorithm(key)
        user_key.size = self._validate_size(key, user_key.algorithm)
        user_key.fingerprint = key.fpr
        user_key.key = data

        return user_key


class Key(models.Model):
    objects = KeyManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.TextField(verbose_name=_('OpenGPG key'))
    fingerprint = models.TextField(max_length=40, verbose_name=_('Fingerprint'))
    last_updated = models.DateTimeField(verbose_name=_('Last update on'),
                                        auto_now=True)

    # We store here the algorithm and the size to avoid creating a
    # GnuPG to get those information each time a user loads its
    # profile.
    algorithm = models.ForeignKey(GPGAlgo, on_delete=models.SET_NULL,
                                  blank=True, null=True,
                                  verbose_name=_('Type'))
    size = models.PositiveSmallIntegerField(verbose_name=_('Size'))

    # This method is transactionally atomic in order to perform an 'update' by
    # actually doing an 'delete' followed by an 'insert' in the same transaction
    @transaction.atomic
    def update_subkeys(self):
        keyring = KeyManager().import_key(self.key)

        SubKey.objects.filter(key=self).delete()

        for fingerprint in keyring.subkeys.keys():
            subkey = SubKey(key=self, fingerprint=fingerprint)
            subkey.full_clean()
            subkey.save()
            log.info(f'Binding fingerprint {fingerprint} to key '
                     f'{self.fingerprint}')


class SubKey(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    fingerprint = models.TextField(max_length=40, verbose_name=_('Fingerprint'))
