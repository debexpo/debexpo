#   makemessages.py - override of django's built-in command
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2022 Baptiste Beauplat <lyknode@debian.org>
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

from glob import glob
from os import chdir, makedirs, unlink, rename
from os.path import abspath, join, dirname, exists
from pathlib import Path
from shutil import copy

from django.core.management.commands.makemessages import STATUS_OK, \
    Command as MakeMessages, normalize_eols
from django.core.management.utils import popen_wrapper
from django.core.management.base import CommandError


class Command(MakeMessages):
    msgmerge_options = ['-q', '--backup=none', '--previous', '--update']

    def handle(self, *args, **kwargs):
        kwargs['keep_pot'] = True
        kwargs['add_location'] = 'file'

        chdir(abspath(join(dirname(__file__), '..', '..', '..')))

        super().handle(*args, **kwargs)

    def _backup_potfiles(self):
        backup_potfiles = []

        for potfile in glob('**/*.pot', recursive=True):
            potfile = abspath(potfile)
            backup = f'{potfile}.bak'

            if exists(potfile):
                copy(potfile, backup)

                backup_potfiles.append(backup)

        return backup_potfiles

    def _skip_header(self, fh):
        while len(fh.readline()[:-1]):
            pass

    def _compare_files(self, file1, file2):
        with open(file1, 'r') as file1_fh, \
             open(file2, 'r') as file2_fh:
            self._skip_header(file1_fh)
            self._skip_header(file2_fh)

            for line1 in file1_fh.readlines():
                line2 = file2_fh.readline()

                if line1 != line2:
                    return True

        return False

    def _restore_unmodified_potfiles(self, potfiles, backup_potfiles):
        index = 0
        potfiles = sorted(set(potfiles))
        backup_potfiles = sorted(backup_potfiles)

        for index, potfile in enumerate(potfiles):
            backup_potfile = backup_potfiles[index]

            modified = self._compare_files(potfile, backup_potfile)

            if modified:
                unlink(backup_potfile)
            else:
                unlink(potfile)
                rename(backup_potfile, potfile)

            index += 1

    def build_potfiles(self):
        backup_potfiles = self._backup_potfiles()
        potfiles = super().build_potfiles()
        self._restore_unmodified_potfiles(potfiles, backup_potfiles)

        return potfiles

    # This code is a modified copy of the original makemessages command from
    # django source code available at:
    #
    # https://github.com/django/django/blob/3.2.16/django/core/management/commands/makemessages.py
    #
    # Patched with:
    # https://github.com/django/django/commit/4bfe8c0eec835b8eaffcda7dc1e3b203751a790a
    #
    # You may safely remove it for use with django >= 4.1.3.
    #
    # SPDX-License-Identifier: BSD-3-Clause
    def write_po_file(self, potfile, locale):
        """
        Create or update the PO file for self.domain and `locale`.
        Use contents of the existing `potfile`.

        Use msgmerge and msgattrib GNU gettext utilities.
        """
        basedir = join(dirname(potfile), locale, 'LC_MESSAGES')
        makedirs(basedir, exist_ok=True)
        pofile = join(basedir, '%s.po' % self.domain)

        if exists(pofile):
            args = ['msgmerge'] + self.msgmerge_options + [pofile, potfile]
            _, errors, status = popen_wrapper(args)
            if errors:
                if status != STATUS_OK:
                    raise CommandError(
                        "errors happened while running msgmerge\n%s" % errors)
                elif self.verbosity > 0:
                    self.stdout.write(errors)
            msgs = Path(pofile).read_text(encoding='utf-8')
        else:
            with open(potfile, encoding='utf-8') as fp:
                msgs = fp.read()
            if not self.invoked_for_django:
                msgs = self.copy_plural_forms(msgs, locale)
        msgs = normalize_eols(msgs)
        msgs = msgs.replace(
            "#. #-#-#-#-#  %s.pot (PACKAGE VERSION)  #-#-#-#-#\n" % self.domain,
            "")
        with open(pofile, 'w', encoding='utf-8') as fp:
            fp.write(msgs)

        if self.no_obsolete:
            args = ['msgattrib'] + self.msgattrib_options + ['-o', pofile,
                                                             pofile]
            msgs, errors, status = popen_wrapper(args)
            if errors:
                if status != STATUS_OK:
                    raise CommandError(
                        "errors happened while running msgattrib\n%s" % errors)
                elif self.verbosity > 0:
                    self.stdout.write(errors)
