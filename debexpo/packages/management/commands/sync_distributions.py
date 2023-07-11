#   sync_distributions.py - commands to sync distributions list from distro-info
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2023 Baptiste Beauplat <lyknode@debian.org>
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

from importlib import import_module
from re import search

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from debexpo.packages.models import Distribution, Project


class Command(BaseCommand):
    help = 'Sync distributions list from distro-info'

    def add_arguments(self, parser):
        parser.add_argument('-N', '--no-confirm',
                            action='store_true',
                            help='Do not prompt for confirmation')
        parser.add_argument('-n', '--dry-run',
                            action='store_true',
                            help='Print modification '
                                 'without making any changes')
        parser.add_argument('--no-cleanup',
                            action='store_true',
                            help='Do not remove old distributions')
        parser.add_argument('--no-create',
                            action='store_true',
                            help='Do not add new distributions')
        parser.add_argument('--exclude',
                            action='append',
                            help='Exclude regex from distribution list')

    def _get_distro_info(self):
        vendor_module = f'{settings.DISTRO_INFO_VENDOR.capitalize()}DistroInfo'

        try:
            DistroInfo = import_module('distro_info')
            VendorInfo = getattr(DistroInfo, vendor_module)
        except (ImportError, AttributeError) as e:
            raise CommandError(f'Failed to import module {vendor_module}: {e}')

        return VendorInfo()

    def _resolve_aliases(self, distro_info):
        aliases = {}

        for alias, target in settings.SUITE_ALIASES.items():
            if target is None:
                aliases[alias] = distro_info.codename(alias)
            else:
                aliases[alias] = target

        return aliases

    def _build_distributions(self, suite):
        distributions = [suite]

        for suffix in settings.DISTRIBUTION_SUFFIX:
            distributions.append(f'{suite}{suffix}')

        return distributions

    def _exclude_from_distributions(self, excludes, distributions):
        filtered = set()

        if excludes is None:
            excludes = []

        for item in list(distributions):
            found = False

            for exclude in excludes:
                if search(rf'{exclude}', item):
                    found = True
                    break

            if not found:
                filtered.add(item)

        return filtered

    def _get_ref_distributions(self, excludes):
        distributions = list(settings.STATIC_SUITES)
        distro_info = self._get_distro_info()
        aliases = self._resolve_aliases(distro_info)

        for suite in distro_info.supported():
            if suite not in settings.STATIC_SUITES:
                distributions.extend(self._build_distributions(suite))

        for alias, target in aliases.items():
            if target not in settings.STATIC_SUITES:
                distributions.extend(self._build_distributions(alias))
            else:
                distributions.append(alias)

        return self._exclude_from_distributions(excludes, distributions)

    def _format_dists(self, title, dists):
        return '\n  '.join([title] + dists) + '\n'

    def _get_db_distributions(self, excludes):
        distributions = [str(dist) for dist in Distribution.objects.all()]

        return self._exclude_from_distributions(excludes, distributions)

    def handle(self, *args, **kwargs):
        ref_dists = self._get_ref_distributions(kwargs['exclude'])
        db_dists = self._get_db_distributions(kwargs['exclude'])
        add_dists = sorted(ref_dists - db_dists)
        del_dists = sorted(db_dists - ref_dists)

        if not kwargs['no_create']:
            print(self._format_dists('Adding new distributions:', add_dists))

        if not kwargs['no_cleanup']:
            print(self._format_dists('Removing old distributions:', del_dists))

        if kwargs['dry_run']:
            return

        # Exclude user interaction from coverage
        if not kwargs['no_confirm']:  # pragma: no cover
            confirm = 'EOF'

            try:
                confirm = input('Confirm modifications? [Y/n] ')
            except EOFError:
                pass

            if confirm not in ['', 'y']:
                return 'Aborting.'

        if not kwargs['no_create']:
            project, _ = Project.objects.get_or_create(
                name=settings.DISTRO_INFO_VENDOR.capitalize())

            for name in add_dists:
                dist = Distribution(name=name, project=project)
                dist.full_clean()
                dist.save()

        if not kwargs['no_cleanup']:
            Distribution.objects.filter(name__in=del_dists).delete()
