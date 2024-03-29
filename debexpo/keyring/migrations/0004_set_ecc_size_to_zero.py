#   0004_set_ecc_size_to_zero.py - Set ECC minimum size to zero
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Baptiste Beauplat <lyknode@debian.org>
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

from django.db import migrations


def set_ecc_size_to_zero(apps, schema_editor):
    set_ecc_size(apps, schema_editor, 0)


def revert_set_ecc_size_to_zero(apps, schema_editor):  # pragma: no cover
    set_ecc_size(apps, schema_editor, 256)


def set_ecc_size(apps, schema_editor, size):
    GPGAlgo = apps.get_model('keyring', 'GPGAlgo')

    algo = GPGAlgo.objects.get(name='ed25519')
    algo.minimal_size_requirement = size
    algo.full_clean()
    algo.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('keyring', '0003_fingerprint_uniqueness',),
    ]

    operations = [
        migrations.RunPython(set_ecc_size_to_zero, revert_set_ecc_size_to_zero),
    ]
