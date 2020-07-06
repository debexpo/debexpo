#   models.py - models for bugs
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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
from re import search
from email.utils import getaddresses
from logging import getLogger
from datetime import timezone
from debianbts import get_status

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

log = getLogger(__name__)


class BugSeverity(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    wishlist = (1, 'Wishlist')
    minor = (2, 'Minor')
    normal = (3, 'Normal')
    important = (4, 'Important')
    serious = (5, 'Serious')
    grave = (6, 'Grave')
    critical = (7, 'Critical')

    @classmethod
    def as_tuple(cls):
        return (cls.wishlist.tuple,
                cls.minor.tuple,
                cls.normal.tuple,
                cls.important.tuple,
                cls.serious.tuple,
                cls.grave.tuple,
                cls.critical.tuple,)


class BugStatus(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    done = (1, 'Done')
    fixed = (2, 'Fixed')
    forwarded = (3, 'Forwarded')
    pending = (4, 'Open')
    pending_fixed = (5, 'Pending')

    @classmethod
    def as_tuple(cls):
        return (cls.done.tuple,
                cls.fixed.tuple,
                cls.pending.tuple,
                cls.pending_fixed.tuple,)


class BugType(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    ITA = (1, 'Intent To Adopt')
    ITP = (2, 'Intent To Package')
    ITS = (3, 'Intent To Salvage')
    O = (4, 'Orphaned')  # noqa: E741
    RFA = (5, 'Request For Adoption')
    RFH = (6, 'Request For Help')
    RFP = (7, 'Request For Package')
    RFS = (8, 'Request For Sponsor')
    bug = (9, 'Bug')

    @classmethod
    def as_tuple(cls):
        return (cls.ITA.tuple,
                cls.ITP.tuple,
                cls.ITS.tuple,
                cls.O.tuple,
                cls.RFA.tuple,
                cls.RFH.tuple,
                cls.RFP.tuple,
                cls.RFS.tuple,
                cls.bug.tuple,)


class BugManager(models.Manager):
    def _guess_bug_type(self, subject):
        type_in_subject = subject.split(':')[0]
        bugtype = getattr(BugType, type_in_subject, None)

        if bugtype:
            return bugtype

        return BugType.bug

    def remove_bugs(self, package):
        self.get_queryset().filter(sources__name=package, bugtype=BugType.bug) \
            .delete()

    def _guess_packages(self, source, subject):
        packages = []

        if source and source not in ('wnpp', 'sponsorship-requests'):
            for name in source.replace(', ', ',').split(','):
                package, _ = BugPackage.objects.get_or_create(name=name)
                packages.append(package)

        else:
            matches = search(r'^\w+:\s+([a-z0-9][a-z0-9.+-]+)', subject)

            if matches:
                name = matches[1]
                package, _ = BugPackage.objects.get_or_create(name=name)
                packages.append(package)

        return packages

    def _extract_email(self, email):
        extract = getaddresses([email])

        if extract:
            return extract[0][1]

    def fetch_bugs(self, numbers):
        bugs = []

        try:
            raw_bugs = get_status(numbers)
        # BTS url is not configurable in debianbts. It cannot be used to trigger
        # an exception from within. Excluded from testing
        except Exception as e:  # pragma: no cover
            log.warning(f'failed to fetch bugs status for {numbers}:\n{str(e)}')
            return []

        for bug in raw_bugs:
            bugtype = self._guess_bug_type(bug.subject)
            status = getattr(BugStatus, bug.pending.replace('-', '_'), None)
            severity = getattr(BugSeverity, bug.severity, None)
            sources = self._guess_packages(bug.source, bug.subject)
            packages = self._guess_packages(bug.package, bug.subject)
            submitter = self._extract_email(bug.originator)
            owner = self._extract_email(bug.owner)
            created = bug.date.replace(tzinfo=timezone.utc)
            updated = bug.log_modified.replace(tzinfo=timezone.utc)

            new = Bug(
                    number=bug.bug_num,
                    bugtype=bugtype,
                    status=status,
                    created=created,
                    updated=updated,
                    severity=severity,
                    subject=bug.subject,
                    submitter_email=submitter,
                    owner_email=owner,
            )

            try:
                new.full_clean(validate_unique=False)
            # Log as warning since this is not supposed to happen
            # Excluded from testing
            except ValidationError as e:  # pragma: no cover
                log.warning('Failed to create a bug from:\n'
                            f'{bug}\n'
                            f'{str(e)}')
            else:
                new.save()
                new.packages.set(packages)
                new.sources.set(sources)
                bugs.append(new)

        return bugs


class BugPackage(models.Model):
    name = models.TextField(unique=True, verbose_name=_('Package name'))


class Bug(models.Model):
    number = models.PositiveIntegerField(unique=True,
                                         primary_key=True,
                                         verbose_name=_('Bug number'))
    bugtype = models.PositiveIntegerField(choices=BugType.as_tuple(),
                                          verbose_name=_('Type'))
    status = models.PositiveIntegerField(choices=BugStatus.as_tuple(),
                                         verbose_name=_('Status'))
    severity = models.PositiveIntegerField(choices=BugSeverity.as_tuple(),
                                           verbose_name=_('Severity'))
    created = models.DateTimeField(verbose_name=_('Creation date'))
    updated = models.DateTimeField(verbose_name=_('Last update date'))
    subject = models.TextField(verbose_name=_('Subject'))
    packages = models.ManyToManyField(BugPackage, related_name='packages_bug')
    sources = models.ManyToManyField(BugPackage, related_name='sources_bug')
    submitter_email = models.TextField(verbose_name=_('Submitter email'))
    owner_email = models.TextField(verbose_name=_('Owner email'), blank=True,
                                   null=True)

    objects = BugManager()

    def is_rc(self):
        return self.severity in (BugSeverity.critical, BugSeverity.grave,
                                 BugSeverity.serious)
