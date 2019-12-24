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
from django.contrib.auth.views import PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetView, LoginView, LogoutView, \
    PasswordResetDoneView
from django.http.response import HttpResponsePermanentRedirect
from django.urls import reverse

from debexpo.base.views import index, contact, intro_reviewers, \
    intro_maintainers, qa
from debexpo.accounts.views import register, profile
from debexpo.accounts.forms import PasswordResetForm
from debexpo.packages.views import package, packages, packages_my, \
    PackagesFeed, sponsor_package, delete_package

urlpatterns = [
    # Base site
    url(r'^$', index, name='index'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^intro-reviewers/$', intro_reviewers, name='reviewers'),
    url(r'^qa/$', qa, name='qa'),
    url(r'^intro-maintainers/$', intro_maintainers, name='maintainers'),

    # Accounts
    url(r'^accounts/reset/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
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
            form_class=PasswordResetForm,
            template_name='password-reset-form.html',
            extra_context={'settings': settings},
        ),
        name='password_reset'),
    url(r'accounts/password_reset/done/$',
        PasswordResetDoneView.as_view(
            template_name='password-reset-done.html',
            extra_context={'settings': settings}
        ),
        name='password_reset_done'),
    url(r'^accounts/register/$', register, name='register'),
    url(r'^accounts/profile/$', profile, name='profile'),

    # Packages
    url(r'^packages/(?P<key>[a-z]+)/(?P<value>.+)/(?P<feed>feed)/$',
        PackagesFeed(),
        name='packages_search_feed'),
    url(r'^packages/(?P<key>[a-z]+)/(?P<value>.+)/$', packages,
        name='packages_search'),
    url(r'^packages/(?P<feed>feed)/$', PackagesFeed(),
        name='packages_feed'),
    url(r'^packages/$', packages,
        name='packages'),

    url(r'^package/(?P<name>.+)/delete/$', delete_package,
        name='delete_package'),
    url(r'^package/(?P<name>.+)/sponsor/$', sponsor_package,
        name='sponsor_package'),
    url(r'^package/(?P<name>.+)/$', package, name='package'),

    # Redirects
    url(r'^my/$', lambda request: HttpResponsePermanentRedirect(
        reverse('profile')), name='my'),
    url(r'^package/$', lambda request: HttpResponsePermanentRedirect(
        reverse('packages')), name='package_index'),
    url(r'^packages/my/$', packages_my, name='packages_my'),
    url(r'^accounts/$', lambda request: HttpResponsePermanentRedirect(
        reverse('profile')), name='accounts')
]
