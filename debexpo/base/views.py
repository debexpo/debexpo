#   views.py - Views for base website
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

import logging

from subprocess import check_output, CalledProcessError
from os.path import dirname, abspath

from django.shortcuts import render
from django.conf import settings

log = logging.getLogger(__name__)


def get_debexpo_version():
    """
    Returns the commit SHA if debexpo runs inside a git repository

    Otherwise, return None
    """
    command = 'git'
    args = ['rev-parse', 'HEAD']
    output = None

    try:
        output = check_output([command] + args,
                              cwd=dirname(abspath(__file__)),
                              text=True)
    except FileNotFoundError:
        log.debug('git not found, skip revision detection.')
    except CalledProcessError:
        log.debug('not a git repository, skip revision detection.')

    return output


def index(request):
    settings.VERSION = get_debexpo_version()

    return render(request, 'index.html', {
        'settings': settings
    })


def contact(request):
    return render(request, 'contact.html', {
        'settings': settings
    })


def intro_reviewers(request):
    return render(request, 'reviewers.html', {
        'settings': settings
    })


def qa(request):
    return render(request, 'qa.html', {
        'settings': settings
    })


def intro_maintainers(request):
    return render(request, 'intro-maintainers.html', {
        'settings': settings
    })
