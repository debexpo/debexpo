# -*- coding: utf-8 -*-
#
#   base.py — The base Controller API
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Holds the base Controller API.

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner, Copyright © 2011 Arno Töll'
__license__ = 'MIT'

# Monkey patch NilAccept from webob for compatibility.
import webob.acceptparse
webob.acceptparse.NilAccept._parsed = property(lambda *args, **kwargs: [])

from pylons import tmpl_context as c, cache, config, app_globals, request, \
    response, session, url
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_, get_lang, set_lang
from pylons.templating import render_mako as render

import debexpo.model as model
from debexpo.model import meta

class SubMenu(object):
    """
    A sub menu class, to be instantiated by controller.
    This class holds several data structures which are parsed by the template engine and
    result in a per-controller sub menu.
    The controller only needs to feed this menu.
    """
    def __init__(self):
        self._label = None
        self._menu = []
        self._entries = []
        self._has_menu = False
        self._menu_label = None

    def has_menu(self):
        return self._has_menu

    def has_label(self):
        return self._label != None

    def has_submenu(self):
        return len(self._menu) > 0

    def set_label(self, label):
        self._has_menu = True
        self._label = label

    def add_menu(self, label, menu):
        if not isinstance(menu, SubMenu):
            raise AttributeError("%s is not an instance of SubMenu" % (menu))
        self._has_menu = True
        self._menu_label = label
	self._menu.append(menu)

    def add_entry(self, label, link):
        self._has_menu = True
        self._entries.append( (label, link) )

    def submenulabel(self):
        return self._menu_label

    def label(self):
        return self._label

    def entries(self):
        for e in self._entries:
            yield e

    def menus(self):
        for e in self._menu:
            yield e

class BaseController(WSGIController):
    """
    Base controller class for all other controllers to extend.
    """

    requires_auth = False

    def __before__(self):
        # Set language according to what the browser requested
        user_agent_language = request.languages[0][0:2]
        if user_agent_language in app_globals.supported_languages:
            set_lang(user_agent_language)
        else:
            set_lang(app_globals.default_language)

        if self.requires_auth and 'user_id' not in session:
            # Remember where we came from so that the user can be sent there
            # after a successful login
            session['path_before_login'] = request.path_info
            session.save()
            redirect(url(controller='login', action='index'))

        c.config = config
        # The templates require the submenu to be existing
        # If no controller added a submenu, its fair enough to instantiate an empty
        # object here
        if not hasattr(c, 'submenu'):
            c.submenu = SubMenu()

    def __call__(self, environ, start_response):
        """
        Invokes the Controller.
        """
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        c.feed_url = None
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.session.remove()

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
