# -*- coding: utf-8 -*-
#
#   py.template - template for new .py files
#
#   This file is part of debexpo
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'


class Dsc:

    def __init__(self, dsc):
        self.dsc = dsc

    def get_dsc_item(self, comp_func):
        if self.dsc and 'Checksums-Sha256' in self.dsc:
            orig_match = list(item for item in self.dsc['Checksums-Sha256'] if
                              comp_func(item))
            if len(orig_match) > 0:
                return orig_match[0]

        return None

    @classmethod
    def extract_orig_asc(self, item):
        return (item.get('name') is not None and (
                item.get('name').endswith('orig.tar.gz.asc') or
                item.get('name').endswith('orig.tar.bz2.asc') or
                item.get('name').endswith('orig.tar.xz.asc')))

    @classmethod
    def extract_orig(self, item):
        return (item.get('name') is not None and (
                item.get('name').endswith('orig.tar.gz') or
                item.get('name').endswith('orig.tar.bz2') or
                item.get('name').endswith('orig.tar.xz')))
