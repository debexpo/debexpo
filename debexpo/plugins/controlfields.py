# -*- coding: utf-8 -*-
#
#   controlfields.py — controlfields plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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

"""
Holds the controlfields plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from debian import deb822
import logging

from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

fields = ['Homepage', 'Vcs-Browser', 'Vcs-Git', 'Vcs-Svn', 'Vcs-Bzr', 'Vcs-Hg']

def _gen_outcomes():
    outcomes = {}

    for field in fields:
        for isisnot in ['', '-not']:
            outcomes['%s-is%s-present' % (field.lower(), isisnot)] = \
                'The %s field is%s present in debian/control' % (field, isisnot.replace('-', ' '))

    return outcomes

class ControlFieldsPlugin(BasePlugin):

    def test_control_fields(self):
        """
        Checks whether additional debian/control fields are present.
        """
        log.debug('Checking whether additional debian/control fields are present')

        try:
            dsc = deb822.Dsc(file(self.changes.get_dsc()))
        except:
            log.critical('Could not open dsc file; skipping plugin')
            return

        for item in fields:
            if item in dsc:
                self.info('%s-is-present' % item.lower(), '%s: %s' % (item, dsc[item]))
                log.debug('%s: %s' % (item, dsc[item]))
            else:
                self.info('%s-is-not-present' % item.lower(), None)
                log.debug('%s field is not present' % item)

plugin = ControlFieldsPlugin

outcomes = _gen_outcomes()
