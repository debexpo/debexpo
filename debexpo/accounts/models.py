#   models.py - models for accounts app
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

from email.utils import getaddresses
from enum import Enum

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserStatus(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    contributor = (1, _('Contributor'))
    maintainer = (2, _('Debian Maintainer (DM)'))
    developer = (3, _('Debian Developer (DD)'))

    @classmethod
    def as_tuple(cls):
        return (cls.contributor.tuple,
                cls.maintainer.tuple,
                cls.developer.tuple,)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, name, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must not be null')
        if not name:
            raise ValueError('The given name must not be null')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)

        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        return user

    def create_user(self, email, name, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, name, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, password, **extra_fields)

    def lookup_user_from_address(self, address):
        """
        Lookup a user using an arbitrary formatted email.

        This method is used by Changes to lookup the user of an unsigned upload,
        when allowed. The address is extracted from the .chagnes Changed-By
        field or, if missing, from the Maintainer field.

        The address format (Vincent Time <vtime@example.org>) is decoded using
        email.utils.getaddresses.
        """
        if not address:
            return

        decoded_address = getaddresses([address])
        email = decoded_address[0][1]

        try:
            return self.get(email=email)
        except User.DoesNotExist:
            return


class User(AbstractUser):
    """User model."""

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('full name'), max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class Countries(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL,
                                verbose_name=_('Country'), blank=True,
                                null=True)
    ircnick = models.CharField(max_length=100, blank=True,
                               verbose_name=_('IRC Nickname'))
    jabber = models.EmailField(blank=True, verbose_name=_('Jabber address'))
    status = models.PositiveSmallIntegerField(
        choices=UserStatus.as_tuple(),
        default=UserStatus.contributor.value,
        verbose_name=_('Status')
    )
