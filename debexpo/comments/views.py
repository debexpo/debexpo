#   views.py - views for comments
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

from logging import getLogger

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse

from .forms import SubscriptionForm, CommentForm
from .models import PackageSubscription
from debexpo.packages.models import Package, PackageUpload

log = getLogger(__name__)


@login_required
def subscriptions(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('subscribe_package',
                                    args=[request.POST.get('package')]))

    return render(request, 'subscriptions.html', {
        'settings': settings,
        'subscriptions': PackageSubscription.objects.filter(user=request.user)
        .all()
    })


@login_required
def unsubscribe(request, name):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    sub = get_object_or_404(PackageSubscription, user=request.user,
                            package=name)
    sub.delete()

    return HttpResponseRedirect(reverse('subscriptions'))


@login_required
def subscribe(request, name):
    sub = PackageSubscription.objects.filter(user=request.user,
                                             package=name)
    instance = None

    if sub.exists():
        instance = sub.get()

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=instance)
        package = request.POST.get('next')

        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.package = name
            subscription.save()

            if subscription.can_delete():
                log.info(f'Unsubscribe {request.user.email} for package {name}')
                subscription.delete()
            else:
                log.info(f'Updating subscription for {request.user.email} on '
                         f'{name}: '
                         f'{", ".join(subscription.get_subscriptions())}')

            if package:
                return HttpResponseRedirect(reverse('package', args=[package]))
            else:
                return HttpResponseRedirect(reverse('subscriptions'))
    else:
        form = SubscriptionForm(instance=instance)
        package = request.GET.get('next')

    return render(request, 'subscribe.html', {
        'settings': settings,
        'package': name,
        'next': package,
        'form': form,
    })


@login_required
def comment(request, name):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    upload_id = request.POST.get('upload_id')
    package = get_object_or_404(Package, name=name)
    upload = get_object_or_404(PackageUpload, package=package, pk=upload_id)
    redirect_url = reverse('package', args=[name])
    index = upload.get_index()

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.upload = upload
        comment.save()
        comment.notify(request)

    return HttpResponseRedirect(f"{redirect_url}#upload-{index}")
