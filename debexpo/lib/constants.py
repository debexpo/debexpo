# -*- coding: utf-8 -*-
#
#   constants.py — Application constants
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
debexpo constants.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'


# User constants
USER_TYPE_NORMAL = 1
USER_TYPE_ADMIN = 2

# Type of user
USER_STATUS_NORMAL = 1 # package maintainer
USER_STATUS_DEVELOPER = 2 # official "Debian Developer"
USER_STATUS_MAINTAINER = 3 # official "Debian Maintainer"

# Package constants
PACKAGE_NEEDS_SPONSOR_UNKNOWN = 1
PACKAGE_NEEDS_SPONSOR_NO = 2
PACKAGE_NEEDS_SPONSOR_YES = 3

# Plugin constants
PLUGIN_SEVERITY_INFO = 1
PLUGIN_SEVERITY_WARNING = 2
PLUGIN_SEVERITY_ERROR = 3
PLUGIN_SEVERITY_CRITICAL = 4
PLUGIN_SEVERITY = {
        PLUGIN_SEVERITY_INFO: 'Info',
        PLUGIN_SEVERITY_WARNING: 'Warning',
        PLUGIN_SEVERITY_ERROR: 'Error',
        PLUGIN_SEVERITY_CRITICAL: 'Critical',
    }

PLUGIN_OUTCOME_PASSED = 1
PLUGIN_OUTCOME_FAILED = 2
PLUGIN_OUTCOME_INFO = 3

# Package comments
PACKAGE_COMMENT_OUTCOME_UNREVIEWED = 1
PACKAGE_COMMENT_OUTCOME_NEEDS_WORK = 2
PACKAGE_COMMENT_OUTCOME_PERFECT = 3

PACKAGE_COMMENT_STATUS_NOT_UPLOADED = 1
PACKAGE_COMMENT_STATUS_UPLOADED = 2

# Package subscriptions
SUBSCRIPTION_LEVEL_UPLOADS = 1
SUBSCRIPTION_LEVEL_COMMENTS = 2

#Sponsor metrics
SPONSOR_METRICS_PRIVATE = 0
SPONSOR_METRICS_RESTRICTED = 1
SPONSOR_METRICS_PUBLIC = 2


SPONSOR_CONTACT_METHOD_NONE = 0
SPONSOR_CONTACT_METHOD_EMAIL = 1
SPONSOR_CONTACT_METHOD_IRC = 2
SPONSOR_CONTACT_METHOD_JABBER = 3

SPONSOR_GUIDELINES_TYPE_NONE = 0
SPONSOR_GUIDELINES_TYPE_URL = 1
SPONSOR_GUIDELINES_TYPE_TEXT = 2

SPONSOR_TECHNICAL_REQUIREMENTS = [
    ('CDBS','cdbs', 'Your package makes use of the <a href="http://build-common.alioth.debian.org/">The Common Debian Build System</a>'),
    ('(Plain) debhelper','debhelper', 'Your package makes use of the <a href="http://kitenet.net/~joey/code/debhelper/">debhelper</a> build system'),
    ('(Short) dh-style debhelper', 'dh', 'Your package makes use of short <tt>dh(1)</tt> style build system'),
    ('No build helper / home brewed debian/rules','yadda', 'Your package is using a completely customized, yet <a href="http://www.debian.org/doc/debian-policy/ch-source.html#s-debianrules">policy compliant</a> <tt>debian/rules</tt> file, which does not make use of either debhelper or CDBS.'),
    ('NMUs','nmu', 'Your package is a <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu">NMU</a>'),
    ('QA uploads','qa', 'Your package is a <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu-qa-upload">QA upload</a>'),
    ('Backports','backports', 'Your package is a <a href="http://backports-master.debian.org/">backported package</a>'),
    ('Modified tarballs (but good reasons)','tarballs', 'Your package modified the original source tarball somehow in a way, it does not match the original checksum anymore, but you have a <a href="http://www.debian.org/doc/manuals/developers-reference/best-pkging-practices.html#bpp-origtargz">good reason</a> to do so'),
    ('VCS snapshot tarballs','vcs_tarballs', 'Your package is not based on a original source tarball at all, but is based on a VCS snapshot',),
    ('contrib/non-free packages', 'non_free', 'Your package it targetting the <tt>contrib</tt> or <tt>non-free</tt> branches (<a href="http://www.debian.org/doc/debian-policy/ch-archive.html#s-sections">Information</a>)'),
    ('1.0 format packages', '10_format', 'Your package is using the 1.0 format (the traditional source format that is).'),
    ('3.0 format packages', '30_format', 'Your package is using the <a href="http://wiki.debian.org/Projects/DebSrc3.0">3.0/quilt</a> format.'),
    ('Allow embedded code copies', 'code_copies', 'Your package can <a href="http://www.debian.org/doc/debian-policy/ch-source.html#s-embeddedfiles">makes use of embedded code copies in a reasonable way</a>.'),
    ('DEP-5 copyright', 'dep5', 'Your package does make use of <a href="http://dep.debian.net/deps/dep5/">DEP-5</a> copyright files.'),
    ('Non-DEP5 copyright', 'nodep5', 'Your package does <em>not</em> make use of <a href="http://dep.debian.net/deps/dep5/">DEP-5</a> copyright files.'),
    ('No Lintian cleanliness (but good reasons)', 'lintian', 'Your package is not <a href="http://lintian.debian.org/">Lintian clean</a> down to the informational level, but you have a good reason why not.')
    ]

SPONSOR_SOCIAL_REQUIREMENTS = [
    ('Prospective DM/DD', 'dmdd', 'You are willing to become a <a href="http://wiki.debian.org/DebianMaintainer">Debian Maintainer</a>/<a href="http://wiki.debian.org/DebianDeveloper">Debian Developer</a> some day.'),
    ('(Willing to be) DM', 'dm', 'You are a <a href="http://wiki.debian.org/DebianMaintainer">Debian Maintainer</a> already, or you plan to become one soon.'),
    ('(Willing to enter) NM', 'nm', 'You are in the <a href="https://nm.debian.org/">New Maintainer</a> process to become a developer already, or you plan to apply soon.'),
    ('Signed GPG key', 'gpg', 'Your GPG matches the <a href="http://lists.debian.org/debian-devel-announce/2010/09/msg00003.html">guidelines of the Debian keyring maintainers</a> and/or is signed by any Debian developer.'),
    ('No one time uploads', '1time', 'You want to maintain the package you want to have sponsored in the forseeable future. Your package is not a single shot.'),
    ('Sharing a time zone', 'tz', 'You share a time zone with your sponsors. This can be useful to get together more easily.'),
    ('Possibility to meet-up', 'meetup', 'You are living close to your sponsor and you are willing to meet him eventually'),
    ('Having already packages in Debian', 'maintainer', 'You are living close to your sponsor and you are willing to meet him eventually')
    ]
