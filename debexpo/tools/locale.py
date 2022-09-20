#   locale.py - locale middleware
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2022 Baptiste Beauplat <lyknode@cilg.org>
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

from django.utils import translation
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware


class LocaleMiddleware(DjangoLocaleMiddleware):
    def _activate_translation(self, request, language):
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_request(self, request):
        if 'quick_language' in request.POST:
            request.session['language'] = request.POST['quick_language']
            request.method = 'GET'

        if 'language' in request.POST:
            if 'language' in request.session:
                del request.session['language']

            self._activate_translation(request, request.POST['language'])

        elif 'language' in request.session and request.session['language']:
            self._activate_translation(request, request.session['language'])

        elif request.user \
                and request.user.is_authenticated \
                and hasattr(request.user, 'profile') \
                and request.user.profile.language:
            self._activate_translation(request, request.user.profile.language)

        else:
            super().process_request(request)
