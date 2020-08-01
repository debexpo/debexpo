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
from django.urls import reverse, include
from django.views.static import serve
from rest_framework_extensions.routers import ExtendedDefaultRouter

from debexpo.base.views import index, contact, intro_reviewers, \
    intro_maintainers, qa, sponsor_overview, sponsor_guidelines, sponsor_rfs
from debexpo.accounts.views import register, profile
from debexpo.accounts.forms import PasswordResetForm
from debexpo.packages.views import package, packages, packages_my, \
    PackagesFeed, sponsor_package, delete_package, delete_upload, \
    PackageViewSet, PackageUploadViewSet
from debexpo.comments.views import subscribe, unsubscribe, subscriptions, \
    comment
from debexpo.importer.views import upload

api = ExtendedDefaultRouter()
api.register(r'packages', PackageViewSet) \
    .register(r'uploads', PackageUploadViewSet,
              'packages-upload', ['package_id'])
api.register(r'uploads', PackageUploadViewSet)

urlpatterns = [
    # Base site
    url(r'^$', index, name='index'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^intro-reviewers/$', intro_reviewers, name='reviewers'),
    url(r'^qa/$', qa, name='qa'),
    url(r'^intro-maintainers/$', intro_maintainers, name='maintainers'),
    url(r'^sponsors/$', sponsor_overview, name='sponsors'),
    url(r'^sponsors/guidelines/$', sponsor_guidelines, name='guidelines'),
    url(r'^sponsors/rfs-howto/(?P<name>.+)/$', sponsor_rfs, name='package_rfs'),
    url(r'^sponsors/rfs-howto/$', sponsor_rfs, name='rfs'),

    # Api
    url(r'^api/', include(api.urls)),

    # Accounts
    url(r'^accounts/reset/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]+-[0-9A-Za-z]+)/$',
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
    url(r'^accounts/subscriptions/$', subscriptions, name='subscriptions'),

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

    url(r'^package/(?P<name>.+)/delete/(?P<upload>[0-9]+)/$', delete_upload,
        name='delete_upload'),
    url(r'^package/(?P<name>.+)/delete/$', delete_package,
        name='delete_package'),
    url(r'^package/(?P<name>.+)/sponsor/$', sponsor_package,
        name='sponsor_package'),
    url(r'^package/(?P<name>.+)/subscribe/$', subscribe,
        name='subscribe_package'),
    url(r'^package/(?P<name>.+)/unsubscribe/$', unsubscribe,
        name='unsubscribe_package'),
    url(r'^package/(?P<name>.+)/comment/$', comment,
        name='comment_package'),
    url(r'^package/(?P<name>.+)/$', package, name='package'),

    # Upload
    url(r'^upload/(?P<name>.+)$', upload, name='upload'),

    # Redirects
    url(r'^my/$', lambda request: HttpResponsePermanentRedirect(
        reverse('profile')), name='my'),
    url(r'^package/$', lambda request: HttpResponsePermanentRedirect(
        reverse('packages')), name='package_index'),
    url(r'^packages/my/$', packages_my, name='packages_my'),
    url(r'^accounts/$', lambda request: HttpResponsePermanentRedirect(
        reverse('profile')), name='accounts'),

    # Repository
    url(r'^debian/(?P<path>.*)$', serve, {
        'document_root': settings.REPOSITORY,
    }, name='debian'),
]
