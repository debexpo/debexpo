#   copyright.py - copyright parsing
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

from debian.copyright import Copyright as DebianCopyright, \
    MachineReadableFormatError, NotMachineReadableError


class ExceptionCopyright(Exception):
    def __str__(self):
        message = super().__str__()
        return f'Failed to parse debian/copyright: {message}'


class Copyright():
    def __init__(self, filename):
        self.copyright = self._parse_copyright(filename)
        self._build_copyright()

    def _parse_copyright(self, filename):
        copyright = None

        try:
            fd = open(filename, 'r')
        # After dpkg 1.20.0, this will be catched by dpkg-source -x
        except IOError:  # pragma: no cover
            return copyright

        with fd:
            try:
                copyright = DebianCopyright(fd)
            except (MachineReadableFormatError, ValueError) as e:
                raise ExceptionCopyright(e)
            except NotMachineReadableError:
                pass

        return copyright

    def _build_copyright(self):
        try:
            self.licenses = self._get_licenses()
            self.author = self._get_author()
        except MachineReadableFormatError as e:
            raise ExceptionCopyright(e)

    def validate(self):
        # Validated by the _parse_copyright method
        pass

    def _get_licenses(self):
        licenses = set()

        if not self.copyright:
            return licenses

        for paragraph in self.copyright.all_files_paragraphs():
            if paragraph.license and paragraph.license.synopsis:
                if not paragraph.files == ('debian/*',):
                    licenses.update([paragraph.license.synopsis])

        return licenses

    def _get_author(self):
        if self.copyright and self.copyright.header and \
                self.copyright.header.upstream_contact:
            return self.copyright.header.upstream_contact[0]

        return None
