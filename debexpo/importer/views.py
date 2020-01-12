#   views.py - upload view
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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

from logging import getLogger

from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, \
    HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt

from debexpo.importer.models import Spool, ExceptionSpoolUploadDenied, \
    ExceptionSpool

log = getLogger(__name__)


@csrf_exempt
def upload(request, name):
    if request.method != 'PUT':
        return HttpResponseNotAllowed(['PUT'])

    try:
        spool = Spool(settings.UPLOAD_SPOOL)
        fd = spool.upload(name)
    except ExceptionSpoolUploadDenied as e:
        return HttpResponseForbidden(e)
    except ExceptionSpool as e:
        return HttpResponseServerError(e)

    while True:
        chunk = request.read(4 * 1024 * 1024)

        if not chunk:
            break

        fd.write(chunk)

    log.info(f'New upload: {fd.name}')
    return HttpResponse()
