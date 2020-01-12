#   control.py — Manage debian control files
#
#   This file is part of debexpo -
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

from os.path import join

from debexpo.tools.files import CheckSumedFile


def parse_section(section):
    """
    Works out the component and section from the "Section" field.
    Sections like `python` or `libdevel` are in main.
    Sections with a prefix, separated with a forward-slash also show the
    component.
    It returns a list of strings in the form [component, section].

    For example, `non-free/python` has component `non-free` and section
    `python`.

    ``section``
        Section name to parse.
    """
    if '/' in section:
        component, thesection = section.split('/', 1)
        if component not in ("main", "contrib", "non-free"):
            return ['main', section.replace('/', '_')]
        else:
            return [component, thesection]
    else:
        return ['main', section]


class ControlFiles():
    METHODS = (
        ('sha256', 'Checksums-Sha256'),
        ('sha512', 'Checksums-Sha512'),
    )

    def __init__(self, basepath, data):
        self.debs = []
        self.files = []

        for entry in data.get('Files', []):
            if 'name' in entry and entry['name']:
                sumed_file = self._build_file(basepath, entry)

                self._add_checksums(sumed_file, data, entry)
                self.files.append(sumed_file)

    def validate(self):
        for sumed_file in self.files:
            sumed_file.validate()

    def _build_file(self, basepath, entry):
        sumed_file = CheckSumedFile(join(basepath, entry['name']))

        sumed_file.size = entry.get('size')
        sumed_file.component = None
        sumed_file.section = entry.get('section')
        sumed_file.priority = entry.get('priority')

        if sumed_file.section:
            sumed_file.component, sumed_file.section = \
                parse_section(sumed_file.section)

        return sumed_file

    def _add_checksums(self, sumed_file, data, entry):
        for method, key in self.METHODS:
            if key in data:
                sumed_file.add_checksum(method, [
                    item[method] for item in data[key]
                    if item.get('name') == entry['name']
                ][0])
