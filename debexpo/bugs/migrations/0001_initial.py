#   0001_initial.py - data model for bugs
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(
                    unique=True, verbose_name='Bug number')),
                ('type', models.PositiveIntegerField(
                    choices=[(1, 'Intent To Adopt'), (2, 'Intent To Package'),
                             (3, 'Intent To Salvage'), (4, 'Orphaned'),
                             (5, 'Request For Adoption'),
                             (6, 'Request For Help'),
                             (7, 'Request For Package'),
                             (8, 'Request For Sponsor'),
                             (9, 'Bug')], verbose_name='Type')),
                ('status', models.PositiveIntegerField(
                    choices=[(1, 'Done'), (2, 'Fixed'), (4, 'Open'),
                             (5, 'Pending')], verbose_name='Status')),
                ('created', models.DateTimeField(verbose_name='Creation date')),
                ('updated', models.DateTimeField(
                    verbose_name='Last update date')),
                ('severity', models.PositiveIntegerField(
                    choices=[(1, 'Wishlist'), (2, 'Minor'), (3, 'Normal'),
                             (4, 'Important'), (5, 'Serious'), (6, 'Grave'),
                             (7, 'Critical')], verbose_name='Severity')),
                ('subject', models.TextField(verbose_name='Subject')),
                ('package', models.TextField(verbose_name='Package')),
                ('submitter_email', models.TextField(
                    verbose_name='Submitter email')),
                ('owner_email', models.TextField(blank=True, null=True,
                                                 verbose_name='Owner email')),
            ],
        ),
    ]
