#   changelog.py - changelog parsing
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Changelog © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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
#   The above changelog notice and this permission notice shall be
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

from debian.changelog import ChangelogParseError, Changelog as DebianChangelog


class ExceptionChangelog(Exception):
    pass


class Changelog():
    def __init__(self, filename):
        self.changelog = self._parse_changelog(filename)
        self._build_changelog()

    def _build_changelog(self):
        self.changes = str(self.changelog._blocks[0])
        self.closes = ' '.join(map(str, self.changelog._blocks[0].bugs_closed))
        self.date = self.changelog._blocks[0].date
        self.version = self.changelog._blocks[0].version
        self.distribution = self.changelog._blocks[0].distributions

    def _parse_changelog(self, filename):
        changelog = None

        try:
            fd = open(filename, 'r')
        except IOError as e:
            raise ExceptionChangelog(e)

        with fd:
            try:
                changelog = DebianChangelog(fd, strict=True)
            except ChangelogParseError as e:
                raise ExceptionChangelog(e)

        return changelog

    # Changelog validation is left to debian.changelog
    def validate(self):
        pass
