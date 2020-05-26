#   rfs.py - collect information for RFS template plugin
#
#   Copyright © 2016 Hayashi Kentaro <kenhys@gmail.com>
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

from debexpo.plugins.models import BasePlugin, PluginSeverity


class PluginRFS(BasePlugin):
    @property
    def name(self):
        return 'rfs'

    def run(self, changes, source):
        """
        Tests whether there are enough information for RFS template.

        This plugin collects:

        - Upstream Author (from debian/copyright)
        - License (from debian/copyright)
        """
        outcome = "d/copyright is in DEP5 format"
        severity = PluginSeverity.info

        author = getattr(source.copyright, 'author')
        licenses = getattr(source.copyright, 'licenses')

        if not author:
            outcome = "Upstream-Contact missing from d/copyright"
            severity = PluginSeverity.warning

        if not licenses:
            licenses = None
            outcome = "d/copyright is not in DEP5 format"
            severity = PluginSeverity.error
        else:
            licenses = ', '.join(licenses)

        data = {
            'author': author,
            'licenses': licenses,
        }

        self.add_result('copyright', outcome, data, severity)
