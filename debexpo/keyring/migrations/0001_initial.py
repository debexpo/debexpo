#   0001_initial.py - Initial db schema for keyring
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


def create_gpg_algorithms(apps, schema_editor):
    gpg_algo = (
        ('rsa', 1, 4096),
        ('ed25519', 22, None),
    )

    GPGAlgo = apps.get_model('keyring', 'GPGAlgo')

    for name, gpg_algorithm_id, size in gpg_algo:
        algo = GPGAlgo()
        algo.name = name
        algo.gpg_algorithm_id = gpg_algorithm_id
        algo.minimal_size_requirement = size
        algo.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GPGAlgo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=10, verbose_name='Type')),
                ('gpg_algorithm_id', models.PositiveSmallIntegerField(
                    verbose_name='GPG Algorithm ID'
                )),
                ('minimal_size_requirement', models.PositiveSmallIntegerField(
                    blank=True, null=True,
                    verbose_name='Minimal size requirment'
                )),
            ],
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('key', models.TextField(verbose_name='OpenGPG key')),
                ('fingerprint', models.TextField(max_length=40,
                                                 verbose_name='Fingerprint')),
                ('last_updated', models.DateTimeField(
                    auto_now=True, verbose_name='Last update on'
                )),
                ('size', models.PositiveSmallIntegerField(verbose_name='Size')),
                ('algorithm', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='keyring.GPGAlgo', verbose_name='Type'
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
        migrations.RunPython(create_gpg_algorithms),
    ]
