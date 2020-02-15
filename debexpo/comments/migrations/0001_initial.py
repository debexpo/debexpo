#   0001_initial.py - migration script for comments
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
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('packages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('package', models.CharField(max_length=100,
                                             verbose_name='Name')),
                ('on_upload', models.BooleanField(
                    verbose_name='Subscribe to uploads')),
                ('on_comment', models.BooleanField(
                    verbose_name='Subscribe to comments')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'package')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            options={'ordering': ['date']},
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Comment')),
                ('date', models.DateTimeField(auto_now_add=True,
                                              verbose_name='Comment date')),
                ('outcome', models.PositiveSmallIntegerField(
                    choices=[(1, 'Not reviewed'),
                             (2, 'Needs work'),
                             (3, 'Ready')], verbose_name='Upload outcome')),
                ('uploaded', models.BooleanField(
                    verbose_name='Uploaded to debian')),
                ('upload', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='packages.PackageUpload')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
