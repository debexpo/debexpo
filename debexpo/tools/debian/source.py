#   source.py - representation of a Debian source package
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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

from logging import getLogger
from subprocess import TimeoutExpired, CalledProcessError, STDOUT
from os.path import join, dirname
from tempfile import TemporaryDirectory

from django.conf import settings

from debexpo.tools.debian.changelog import Changelog, ExceptionChangelog
from debexpo.tools.debian.copyright import Copyright, ExceptionCopyright
from debexpo.tools.debian.control import Control, ExceptionControl
from debexpo.tools.proc import debexpo_exec

log = getLogger(__name__)


class ExceptionSource(Exception):
    pass


class Source():
    def __init__(self, dsc):
        self.dsc = dsc
        self.temp_dir = TemporaryDirectory(dir=dirname(self.dsc.filename))
        self.source_dir = join(self.temp_dir.name, 'source')

    def extract(self):
        args = ['-x', str(self.dsc), self.source_dir]

        try:
            debexpo_exec('dpkg-source', args,
                         stderr=STDOUT,
                         cwd=dirname(self.dsc.filename),
                         text=True)
        except FileNotFoundError:  # pragma: no cover
            log.error('dpkg-source not found')
            raise ExceptionSource('Internal error. Please contact debexpo '
                                  f'administrators at {settings.SUPPORT_EMAIL}')
        except CalledProcessError as e:
            raise ExceptionSource('Could not extract source package from '
                                  f'{str(self.dsc)}: {e.output}')
        except TimeoutExpired:
            raise ExceptionSource('Could not extract source package from '
                                  f'{str(self.dsc)}: extraction took too long')

    def get_source_dir(self):
        return self.source_dir

    def parse_control_files(self):
        try:
            self.changelog = Changelog(join(self.get_source_dir(),
                                            'debian', 'changelog'))
            self.copyright = Copyright(join(self.get_source_dir(),
                                            'debian', 'copyright'))
            self.control = Control(join(self.get_source_dir(),
                                        'debian', 'control'))
        except (ExceptionChangelog, ExceptionCopyright, ExceptionControl) as e:
            raise ExceptionSource(e)

    def remove(self):
        self.temp_dir.cleanup()
