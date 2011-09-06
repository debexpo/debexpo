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
    ('CDBS','cdbs'),
    ('debhelper','debhelper'),
    ('custom debian/rules','debhelper'),
    ('NMUs','nmu'),
    ('QA uploads','qa'),
    ('Backports','backports'),
    ('Modified Tarballs','tarballs'),
    ('VCS snapshot tarballs','vcs_tarballs'),
    ('contrib/non-free packages', 'non_free'),
    ('1.0 format packages', '10_format'),
    ('3.0 format packages', '30_format'),
    ('No embedded code copies', 'code_copies'),
    ('DEP-5 copyright', 'dep5'),
    ('Non-DEP5 copyright', 'nodep5'),
    ('Lintian cleanness', 'lintian')
    ]

SPONSOR_SOCIAL_REQUIREMENTS = [
    ('Prospective DM/DD', 'dmdd'),
    ('(Willing to be) DM', 'dm'),
    ('(Willing to enter) NM', 'nm'),
    ('Signed GPG key', 'gpg'),
    ('No one time uploads', '1time'),
    ('Sharing a time zone', 'tz'),
    ('Possibility to meet-up', 'meetup'),
    ('Having already packages in Debian', 'maintainer')
    ]
