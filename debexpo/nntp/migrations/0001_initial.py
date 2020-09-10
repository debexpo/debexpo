#   0001_initial.py - migration script for nntp models
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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
from django.db import migrations, models


def create_gmane_lists(apps, schema_editor):
    NNTPFeed = apps.get_model('nntp', 'NNTPFeed')

    # Last updated on 2020-07-01
    for namespace, name, last in (
                (
                    'remove_uploads',
                    'gmane.linux.debian.backports.changes',
                    '40046',
                ),
                (
                    'remove_uploads',
                    'gmane.linux.debian.devel.changes.unstable',
                    '583845',
                ),
                (
                    'remove_uploads',
                    'gmane.linux.debian.devel.changes.stable',
                    '11992',
                ),
            ):
        feed = NNTPFeed()
        feed.namespace = namespace
        feed.name = name
        feed.last = last

        feed.full_clean()
        feed.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NNTPFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('namespace', models.TextField(verbose_name='Namespace')),
                ('name', models.TextField(verbose_name='List name')),
                ('last', models.TextField(
                    verbose_name='Last message processed')),
            ],
        ),
        migrations.RunPython(create_gmane_lists),
    ]
