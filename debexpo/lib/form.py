# -*- coding: utf-8 -*-
#
#   form.py — Helpers for more complex formencode forms
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
Holds helper functions for dealing with the state in formencode form validation
schemas and validators.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'
__contributors__ = ['Christoph Haas']

import formencode
import logging
import pylons

log = logging.getLogger(__name__)


class State(object):
    """
    Trivial state class to be used by formencode validators to store
    information.

    For example::

      >>> c = State(one='foo', two='bar')
      >>> c.one
      'foo'
      >>> c.two
      'bar'
    """
    def __init__(self, **kw):
        for key in kw:
            setattr(self, key, kw[key])


def validate(schema, **state_kwargs):
    """
    Validate a form against a schema.

    ``schema``
        Schema to validate against.

    ``state_kwargs``
        Arguments to the state.
    """
    if state_kwargs:
        state = State(**state_kwargs)
    else:
        state = None

    log.debug('Validating form against schema %s' % schema)
    return schema.to_python(pylons.request.params, state)


def htmlfill(html, exception_error=None):
    """
    Fill an HTML form with values when a formencode.Invalid exception is thrown.

    ``html``
        Form to fill.

    ``exception_error``
        Invalid exception to use when filling the form.
    """
    return formencode.htmlfill.render(
        form=html,
        defaults=pylons.request.params,
        errors=(exception_error and exception_error.unpack_errors()),
        encoding=pylons.response.determine_charset()
    )
