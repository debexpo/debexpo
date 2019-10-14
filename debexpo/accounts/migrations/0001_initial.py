#   0001_initial.py - initial migration for account app
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Jonny Lamb <jonny@debian.org>
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

import xml.dom.minidom

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def iso_countries():
    parsed = xml.dom.minidom.parse(
        open('/usr/share/xml/iso-codes/iso_3166.xml'))
    entries = parsed.getElementsByTagName('iso_3166_entry')

    for entry in entries:
        if entry.attributes.get('common_name') is not None:
            yield entry.attributes['common_name'].value
        else:
            yield entry.attributes['name'].value


def create_iso_countries(apps, schema_editor):
    Countries = apps.get_model('accounts', 'Countries')

    for name in iso_countries():
        country = Countries()
        country.name = name
        country.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Countries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('ircnick', models.CharField(blank=True, max_length=100,
                                             verbose_name='IRC Nickname')),
                ('jabber', models.EmailField(blank=True, max_length=254,
                                             verbose_name='Jabber address')),
                ('country', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='accounts.Countries',
                    verbose_name='Country'
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
        migrations.RunPython(create_iso_countries),
    ]
