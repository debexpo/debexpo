#   urls.py - debexpo URL Configuration
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

from django.conf import settings
from django.conf.urls import url
from debexpo.base.views import index, contact, intro_reviewers, \
    intro_maintainers, qa
from debexpo.accounts.views import register
from django.contrib.auth.views import PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetView, LoginView, LogoutView, \
    PasswordResetDoneView

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^contact$', contact, name='contact'),
    url(r'^intro-reviewers$', intro_reviewers, name='reviewers'),
    url(r'^qa$', qa, name='qa'),
    url(r'^intro-maintainers$', intro_maintainers, name='maintainers'),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',  # noqa: E501
        PasswordResetConfirmView.as_view(
            template_name='password-reset-confirm.html',
            extra_context={'settings': settings}
        ),
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$',
        PasswordResetCompleteView.as_view(
            template_name='password-reset-complete.html',
            extra_context={'settings': settings}
        ),
        name='password_reset_complete'),
    url(r'accounts/login/$',
        LoginView.as_view(
            template_name='login.html',
            extra_context={'settings': settings}
        ),
        name='login'),
    url(r'accounts/logout/$',
        LogoutView.as_view(
            template_name='logout.html',
            next_page='/',
            extra_context={'settings': settings}
        ),
        name='logout'),
    url(r'accounts/password_reset/$',
        PasswordResetView.as_view(
            template_name='password-reset-form.html',
            email_template_name='password-reset.eml',
            subject_template_name='password-reset-subject.eml',
            extra_context={'settings': settings},
            extra_email_context={'settings': settings}
        ),
        name='password_reset'),
    url(r'accounts/password_reset/done/$',
        PasswordResetDoneView.as_view(
            template_name='password-reset-done.html',
            extra_context={'settings': settings}
        ),
        name='password_reset_done'),
    url(r'^accounts/register$', register, name='register'),
]
