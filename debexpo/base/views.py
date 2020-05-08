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
from datetime import datetime, timedelta, timezone
from re import IGNORECASE, search
from urllib.parse import quote_plus
from html import unescape

from django.shortcuts import render
from django.conf import settings
from django.template.loader import render_to_string

from debexpo.packages.models import Package, PackageUpload
from debexpo.plugins.models import PluginResults
from debexpo.packages.views import _get_timedeltas
from debexpo.bugs.models import Bug, BugSeverity, BugType


log = logging.getLogger(__name__)


def get_debexpo_version():
    """
    Returns the commit SHA if debexpo runs inside a git repository

    Otherwise, return None
    """
    command = 'git'
    args = ['rev-parse', 'HEAD']
    output = None

    # note: testing results depends on wether git is installed or not and if we
    # currently are in a git reposirtory. Hence, this is tested manually.
    try:
        output = check_output([command] + args,
                              cwd=dirname(abspath(__file__)),
                              text=True)
    except FileNotFoundError:  # pragma: no cover
        log.debug('git not found, skip revision detection.')
    except CalledProcessError:  # pragma: no cover
        log.debug('not a git repository, skip revision detection.')

    if output:
        output = output.strip()

    return output


def index(request):
    settings.VERSION = get_debexpo_version()
    max_time = datetime.now(timezone.utc) - timedelta(days=30)
    packages = set(Package.objects
                   .filter(packageupload__uploaded__gte=max_time)
                   .filter(needs_sponsor=True))

    return render(request, 'index.html', {
        'settings': settings,
        'packages': packages,
        'deltas': _get_timedeltas(packages),
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


def sponsor_overview(request):
    return render(request, 'sponsor-overview.html', {
        'settings': settings
    })


def sponsor_guidelines(request):
    return render(request, 'sponsor-guidelines.html', {
        'settings': settings
    })


def get_rfs_categories(upload):
    categories = set()

    for number in upload.closes.split(' '):
        try:
            bug = Bug.objects.get(number=number)
        except (Bug.DoesNotExist, ValueError):
            continue
        else:
            if bug.bugtype != BugType.bug:
                categories.add(BugType(bug.bugtype)._name_)

            if bug.is_rc():
                categories.add('RC')

    if search(r'\bTeam\b\s*\bUpload*\b', upload.changes, flags=IGNORECASE):
        categories.add('Team')

    if search(r'\bQA\b\s*\bUpload*\b', upload.changes, flags=IGNORECASE):
        categories.add('QA')

    if search(r'\bNon\b[\s-]\bMaintainer\b\s*\bUpload*\b', upload.changes,
              flags=IGNORECASE):
        categories.add('NMU')

    if categories:
        return f'[{"] [".join(sorted(categories))}]'

    return ''


def get_rfs_severity(upload, categories):
    if '[RC]' in categories:
        return BugSeverity.important.label.lower()

    if upload.package.in_debian:
        return BugSeverity.normal.label.lower()

    return BugSeverity.wishlist.label.lower()


def sponsor_rfs(request, name=None):
    upload = None
    info = None
    binaries = None
    severity = None
    categories = []

    if name:
        try:
            upload = PackageUpload.objects.filter(package__name=name) \
                .latest('uploaded')
            info = PluginResults.objects.get(upload=upload, plugin='rfs').data
        except (PackageUpload.DoesNotExist, PluginResults.DoesNotExist):
            pass
        else:
            binaries = '\n  '.join(
                upload.package.get_full_description().splitlines())
            categories = get_rfs_categories(upload)
            severity = get_rfs_severity(upload, categories)

    rfs_html = render_to_string('rfs.html', {
        'upload': upload,
        'info': info,
        'binaries': binaries,
        'severity': severity,
        'categories': categories,
        'settings': settings,
    }, request)
    rfs = unescape(rfs_html)
    rfs_encoded = quote_plus(rfs).replace('+', '%20')

    return render(request, 'sponsor-rfs.html', {
        'upload': upload,
        'info': info,
        'binaries': binaries,
        'rfs_encoded': rfs_encoded,
        'severity': severity,
        'categories': categories,
        'settings': settings,
    })
