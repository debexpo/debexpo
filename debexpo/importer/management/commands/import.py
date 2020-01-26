#   importer — django management command to import new packages
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from debexpo.importer.models import Importer
from debexpo.tools.debian.changes import Changes


class Command(BaseCommand):
    help = 'Import new package to debexpo'

    def add_arguments(self, parser):
        parser.add_argument('changes', nargs='+', help='changes file to import')

    def handle(self, *args, **options):
        importer = Importer(repository=settings.REPOSITORY)

        for filename in options['changes']:
            changes = None
            error = None

            try:
                changes = Changes(filename)
                importer.process_upload(changes)
            except Exception as e:
                error = e

            if changes:
                changes.cleanup_source()

            if error:
                raise CommandError(error)

            importer.repository.update()
            self.stdout.write(self.style.SUCCESS(f'Package {changes.source} '
                                                 'imported successfuly'))
