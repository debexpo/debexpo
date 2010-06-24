# -*- coding: utf-8 -*-
#
#   error.py — The application's ErrorController object
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
Holds the ErrorController class.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import cgi
import os.path

import paste.fileapp
from pylons.middleware import error_document_template, media_path
from webhelpers.html.builder import literal

from debexpo.lib.base import *

class ErrorController(BaseController):
    """
    Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """

    def document(self):
        """
        Renders the error document.
        """
        resp = request.environ.get('pylons.original_response')
        c.message = literal(resp.body) or cgi.escape(request.GET.get('message', ''))
        c.code = cgi.escape(request.GET.get('code', str(resp.status_int)))
        response.headers = resp.headers
        return render('/error.mako')

    def img(self, id):
        """
        Serves Pylons' stock images.

        ``id``
            ID of the image requested.
        """
        return self._serve_file(os.path.join(media_path, 'img', id))

    def style(self, id):
        """
        Serves Pylons' stock stylesheets.

        ``id``
            ID of the style requested.
        """
        return self._serve_file(os.path.join(media_path, 'style', id))

    def _serve_file(self, path):
        """
        Calls Paste's FileApp (a WSGI application) to serve the file at the specified path.

        ``path``
            Path of the file to serve.
        """
        fapp = paste.fileapp.FileApp(path)
        return fapp(request.environ, self.start_response)
