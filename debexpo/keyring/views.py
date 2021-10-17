#   views.py - keyring view classes
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Baptiste Beauplat <lyknode@debian.org>
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

from django.views.generic import View
from django.views.generic.detail import BaseDetailView
from django.http import HttpResponseServerError, HttpResponse, \
                        HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from debexpo.keyring.models import Key


class HKPSearchView(BaseDetailView):
    model = Key

    def get(self, request, *args, **kwargs):
        if 'search' not in self.request.GET:
            return HttpResponseBadRequest("Missing 'search' query string")

        try:
            return super().get(request, *args, **kwargs)
        except Key.MultipleObjectsReturned:
            return HttpResponseServerError('Multiple matches found', status=500)

    def get_object(self, queryset=None):
        key_id = self.request.GET['search'].replace('0x', '')

        return get_object_or_404(Key, fingerprint__endswith=key_id)

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(self.object.key + '\n')


class HKPView(View):
    def get(self, request, *args, **kwargs):
        if 'op' not in self.request.GET:
            return HttpResponseBadRequest("Missing 'op' query string")

        if self.request.GET['op'] == 'get':
            return HKPSearchView.as_view()(request)
        else:
            return HttpResponseServerError('Not Implemented', status=501)
