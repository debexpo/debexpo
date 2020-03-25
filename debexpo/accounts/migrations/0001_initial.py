#   0001_initial.py - initial migration for account app
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

import xml.dom.minidom

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import debexpo.accounts.models


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
        country.full_clean()
        country.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('password', models.CharField(
                    max_length=128,
                    verbose_name='password')),
                ('last_login', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    default=False,
                    help_text='Designates that this user has all permissions '
                    'without explicitly assigning them.',
                    verbose_name='superuser status')),
                ('is_staff', models.BooleanField(
                    default=False,
                    help_text='Designates whether the user can log into this '
                    'admin site.',
                    verbose_name='staff status')),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Designates whether this user should be treated '
                    'as active. Unselect this instead of deleting accounts.',
                    verbose_name='active')),
                ('date_joined', models.DateTimeField(
                    default=django.utils.timezone.now,
                    verbose_name='date joined')),
                ('email', models.EmailField(
                    max_length=254,
                    unique=True,
                    verbose_name='email address')),
                ('name', models.CharField(
                    max_length=150,
                    verbose_name='full name')),
                ('groups', models.ManyToManyField(
                    blank=True,
                    help_text='The groups this user belongs to. A user will '
                    'get all permissions granted to each of their groups.',
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.Group',
                    verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(
                    blank=True,
                    help_text='Specific permissions for this user.',
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.Permission',
                    verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', debexpo.accounts.models.UserManager()),
            ],
        ),
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
