#!/usr/bin/python3
#   db-miration-v2-to-v3.py - migration script from debexpo 2 to 3.
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

#   Note that is script is only compatible with PostgreSQL.
#   Use the following procedure to apply:
#
#   NEW_DB=testing
#   OLD_DB=prod
#   OLD_REPO=/old-repo
#   NEW_REPO=/new-repo
#   TIME="$(date +%s)"
#   rsync -a --delete "${OLD_REPO}/" "${NEW_REPO}/"
#   sudo -u postgres dropdb "${NEW_DB}"
#   sudo -u postgres createdb -O "${USER}" -E UTF-8 "${NEW_DB}"
#   mkdir -p -m 0700 ~/export
#   sudo -u postgres pg_dump --no-acl --no-owner "${OLD_DB}" \
#        > ~/export/${OLD_DB}-${TIME}.sql
#   psql "${NEW_DB}" < ~/export/${OLD_DB}-${TIME}.sql
#   python3 ../manage.py migrate
#   ./db-miration-v2-to-v3.py

import django
import os
import sys

from django.db import connection
from os.path import join, dirname, abspath, relpath
from datetime import timezone
from json import loads, dumps
from re import search

# Setup django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'debexpo.settings.debexpo')
sys.path.append(join(dirname(dirname(abspath(__file__)))))
django.setup(set_prefix=False)


# Django imports (has to be after django setup)
from django.conf import settings  # noqa: E402
from django.contrib.auth.models import BaseUserManager  # noqa: E402

from debexpo.accounts.models import User, Profile, Countries  # noqa: E402
from debexpo.keyring.models import Key, GPGAlgo  # noqa: E402
from debexpo.packages.models import Package, PackageUpload, \
                                    BinaryPackage, Distribution, Component, \
                                    SourcePackage, Priority, Section \
                                    # noqa: E402
from debexpo.tools.gnupg import GnuPG, ExceptionGnuPGMultipleKeys  # noqa: E402
from debexpo.comments.models import Comment, PackageSubscription  # noqa: E402
from debexpo.plugins.models import PluginResults, PluginSeverity  # noqa: E402
from debexpo.repository.models import RepositoryFile  # noqa: E402


class PluginTranslator():
    def __init__(self, row):
        self.row = row

    @staticmethod
    def load(row):
        for translator in PLUGIN_TRANSLATORS:
            if translator.translate_for == row[0]:
                return translator(row)

        return PluginTranslator(row)

    @property
    def outcome(self):
        return self.row[1]

    @property
    def test(self):
        return self.plugin

    @property
    def plugin(self):
        return self.row[0]

    @property
    def json(self):
        return dumps(self._normalize_json_keys())

    @property
    def severity(self):
        return PluginSeverity(self.row[3])

    @property
    def skip(self):
        return False

    def _normalize_json_keys(self):
        json = loads(self.row[2])

        for key in list(json.keys()):
            json[key.replace('-', '_')] = json.pop(key)

        return json


class TranslatorDistribution(PluginTranslator):
    translate_for = 'distribution'

    @property
    def test(self):
        return 'check-unreleased'

    @property
    def json(self):
        return dumps({})


class TranslatorNative(PluginTranslator):
    translate_for = 'native'

    @property
    def json(self):
        return dumps({})


class TranslatorBuildSystem(PluginTranslator):
    translate_for = 'buildsystem'

    @property
    def test(self):
        return 'build_system'

    @property
    def json(self):
        return dumps(self._normalize_json_keys())

    @property
    def plugin(self):
        return 'build-system'


class TranslatorControlFields(PluginTranslator):
    translate_for = 'controlfields'

    @property
    def plugin(self):
        return 'control-fields'

    @property
    def test(self):
        return 'control_fields'

    @property
    def json(self):
        return dumps({})


class TranslatorDiffClean(PluginTranslator):
    translate_for = 'diffclean'

    @property
    def plugin(self):
        return 'diff-clean'

    @property
    def test(self):
        return 'diff-stat'

    @property
    def json(self):
        json = self._normalize_json_keys()

        json.pop('dirty')

        return dumps(json)


class TranslatorWatchFile(PluginTranslator):
    translate_for = 'watchfile'

    @property
    def plugin(self):
        return 'watch-file'

    @property
    def test(self):
        return 'uscan'

    @property
    def json(self):
        json = loads(self.row[2])

        works = json.get('watch-file-works', False)
        output = json.get('uscan-output', None)
        json = {}

        if not works:
            json['uscan_output'] = output
        else:
            matches = search(
                r'\bon remote site is (.*), local version is\s+(.*)', output)

            if matches:
                json['upstream'] = matches[1]
                json['local'] = matches[2]
            else:
                json['uscan_output'] = output

            matches = search(r'\bto download is identified as\s+(.*)', output)

            if matches:
                json['url'] = matches[1]

        return dumps(json)


class TranslatorRFS(PluginTranslator):
    translate_for = 'rfstemplate'

    @property
    def plugin(self):
        return 'rfs'

    @property
    def test(self):
        return 'copyright'

    @property
    def json(self):
        origin = loads(self.row[2])

        licenses = origin.get('upstream-license', None)
        author = origin.get('upstream-author', None)

        if licenses == '[fill in]':
            licenses = None

        if author == '[fill in name and email of upstream]':
            author = None

        return dumps({
            'author': author,
            'licenses': licenses,
        })


class TranslatorMaintainerEmail(PluginTranslator):
    translate_for = 'maintaineremail'

    @property
    def plugin(self):
        return 'maintainer-email'


class TranslatorDebianQA(PluginTranslator):
    translate_for = 'debianqa'

    @property
    def plugin(self):
        return 'debian-qa'

    @property
    def json(self):
        json = self._normalize_json_keys()

        if 'latest_upload' in json:
            json['last_upload'] = json.pop('latest_upload')

        return dumps(json)


class TranslatorLintian(PluginTranslator):
    translate_for = 'lintian'

    @property
    def plugin(self):
        return 'lintian'

    @property
    def test(self):
        return 'lintian-tags'

    @property
    def json(self):
        json = loads(self.row[2])

        for first in json.keys():
            for second in json[first].keys():
                for third in json[first][second].keys():
                    tags = []

                    for lines in json[first][second][third]:
                        tags.append(' '.join(lines))

                    json[first][second][third] = tags

        return dumps(json)


class TranslatorClosedBugs(PluginTranslator):
    translate_for = 'closedbugs'

    @property
    def plugin(self):
        return 'closed-bugs'

    @property
    def test(self):
        return 'bugs'

    @property
    def json(self):
        json = loads(self.row[2])

        if 'raw' in json:
            json.pop('raw')

        return dumps(json)


PLUGIN_TRANSLATORS = (
    TranslatorDistribution,
    TranslatorNative,
    TranslatorBuildSystem,
    TranslatorControlFields,
    TranslatorDiffClean,
    TranslatorWatchFile,
    TranslatorRFS,
    TranslatorMaintainerEmail,
    TranslatorDebianQA,
    TranslatorLintian,
    TranslatorClosedBugs,
)


def main():
    # # Normalize previous schema
    drop_unused_tables()
    add_missing_constraints()
    remove_duplicated_emails()
    drop_spam_users()

    # # Import to new schema
    import_users()
    import_packages()
    import_comments()
    import_repository()


def import_repository():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT name,'
            '    version,'
            '    component,'
            '    distribution,'
            '    filename,'
            '    size,'
            '    sha256sum'
            '    FROM package_files'
            '    JOIN source_packages'
            '        ON source_packages.id = package_files.source_package_id'
            '    JOIN package_versions'
            '        ON package_versions.id ='
            '           source_packages.package_version_id'
            '    JOIN packages'
            '        ON packages.id = package_versions.package_id'
            '    WHERE sha256sum != \'\';'
        )

        files = list_all_repository_files()

        for row in cursor.fetchall():
            try:
                import_repository_file(files, row)
            except Exception as e:
                print(f'> Error importing repository: {row[4]}\n> {e}')

        if files:
            print(f'orphan repository files: {files}')


def list_all_repository_files():
    files = set()

    for (root, _, filesnames) in os.walk(join(settings.REPOSITORY, 'pool')):
        for filename in filesnames:
            fpath = join(root, filename)
            files.add(relpath(fpath, settings.REPOSITORY))

    return files


def import_repository_file(files, row):
    try:
        files.remove(row[4])
    except KeyError:
        raise Exception(f'{row[4]}: no such file')

    try:
        repo_file = RepositoryFile.objects.get(path=row[4])
    except RepositoryFile.DoesNotExist:
        repo_file = RepositoryFile()

    repo_file.package = row[0]
    repo_file.version = row[1]
    repo_file.component = Component.objects.get_or_create(
        name=row[2].lower())[0]
    repo_file.distribution = Distribution.objects.get_or_create(
        name=row[3].lower())[0]
    repo_file.path = row[4]
    repo_file.size = row[5]
    repo_file.sha256sum = row[6]

    repo_file.full_clean()
    repo_file.save()


def import_comments():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT text,'
            '    time,'
            '    outcome,'
            '    package_comments.status,'
            '    uploaded,'
            '    email'
            '    FROM package_comments'
            '    LEFT JOIN package_versions'
            '        ON package_comments.package_version_id = '
            '           package_versions.id'
            '    LEFT JOIN users'
            '        ON users.id = package_comments.user_id;'
        )

        for row in cursor.fetchall():
            try:
                import_comment(row)
            except Exception as e:
                print(f'> Error importing comment: {row[0]}\n> {e}')


def import_comment(row):
    try:
        comment = Comment.objects.get(date=row[1].replace(tzinfo=timezone.utc))
    except Comment.DoesNotExist:
        comment = Comment()

    comment.text = row[0]
    comment.outcome = row[2]
    comment.uploaded = True if row[3] == 2 else False
    comment.upload = PackageUpload.objects.get(
        uploaded=row[4].replace(tzinfo=timezone.utc))
    comment.user = User.objects.get(email=row[5])

    comment.full_clean()
    comment.save()

    Comment.objects.filter(id=comment.id).update(
        date=row[1].replace(tzinfo=timezone.utc))


def import_packages():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT ON (name) name,'
            '    needs_sponsor::boolean,'
            '    data,'
            '    description'
            '    FROM packages'
            '    LEFT JOIN package_versions'
            '        ON packages.id = package_versions.package_id'
            '    LEFT JOIN package_info'
            '        ON (package_info.package_version_id = package_versions.id'
            '            AND package_info.from_plugin = \'debianqa\');'
        )

        for row in cursor.fetchall():
            try:
                package = import_package(row)
                import_package_uploads(package, row[3])
            except Exception as e:
                print(f'> Error importing package: {row[0]}\n> {e}')


def import_package_uploads(package, description):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT version,'
            '    rfs.data,'
            '    closes,'
            '    uploaded,'
            '    component,'
            '    distribution,'
            '    email,'
            '    priority,'
            '    section,'
            '    vcs.data,'
            '    maintainer.data'
            '    FROM package_versions'
            '    LEFT JOIN packages'
            '        ON packages.id = package_versions.package_id'
            '    LEFT JOIN users'
            '        ON users.id = packages.user_id'
            '    LEFT JOIN package_info AS rfs'
            '        ON (rfs.package_version_id = package_versions.id'
            '            AND rfs.from_plugin = \'rfstemplate\')'
            '    LEFT JOIN package_info AS vcs'
            '        ON (vcs.package_version_id = package_versions.id'
            '            AND vcs.from_plugin = \'controlfields\')'
            '    LEFT JOIN package_info AS maintainer'
            '        ON (maintainer.package_version_id = package_versions.id'
            '            AND maintainer.from_plugin = \'maintaineremail\')'
            '    WHERE packages.name = %s;',
            [package.name]
        )

        for row in cursor.fetchall():
            try:
                upload = import_package_upload(package, row)
                import_package_source(upload, row)
                import_package_binary(upload, description)
                import_plugins_results(upload)
            except Exception as e:
                print(f'> Error importing package upload: {row[0]}\n> {e}')


def import_plugins_results(upload):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT from_plugin,'
            '    outcome,'
            '    data,'
            '    severity'
            '    FROM package_info'
            '    LEFT JOIN package_versions'
            '        ON package_info.package_version_id = package_versions.id'
            '    WHERE uploaded = %s;',
            [upload.uploaded]
        )

        for row in cursor.fetchall():
            import_plugin_result(upload, row)


def import_plugin_result(upload, row):
    translator = PluginTranslator.load(row)

    if translator.skip:
        return

    try:
        result = PluginResults.objects.get(upload=upload,
                                           plugin=translator.plugin)
    except PluginResults.DoesNotExist:
        result = PluginResults()

    result.plugin = translator.plugin
    result.test = translator.test
    result.outcome = translator.outcome
    result.json = translator.json
    result.severity = translator.severity
    result.upload = upload

    result.full_clean()
    result.save()


def import_package_source(upload, row):
    try:
        source = SourcePackage.objects.get(upload=upload)
    except SourcePackage.DoesNotExist:
        source = SourcePackage()

    vcs = loads(row[9]) if row[9] else {}
    maintainer = loads(row[10]) if row[10] else {}
    if 'Short-Description' in vcs:
        vcs.pop('Short-Description')

    source.upload = upload
    source.maintainer = maintainer.get('maintainer-email',
                                       'Failed to decode maintainer')
    source.homepage = vcs.pop('Homepage') if 'Homepage' in vcs else None
    source.vcs = dumps(vcs)
    source.priority = Priority.objects.get_or_create(name=row[7].lower())[0]
    source.section = Section.objects.get_or_create(name=row[8].lower())[0]

    source.full_clean()
    source.save()


def import_package_upload(package, row):
    try:
        upload = PackageUpload.objects.get(
            uploaded=row[3].replace(tzinfo=timezone.utc))
    except PackageUpload.DoesNotExist:
        upload = PackageUpload()

    json = loads(row[1]) if row[1] else {}

    upload.package = package
    upload.uploader = User.objects.get(email=row[6])
    upload.version = row[0]
    upload.distribution = Distribution.objects.get_or_create(
        name=row[5].lower())[0]
    upload.component = Component.objects.get_or_create(name=row[4].lower())[0]
    upload.changes = json.get('package-changelog', 'Failed to decode changelog')
    upload.closes = row[2] if row[2] else ''

    upload.full_clean()
    upload.save()

    PackageUpload.objects.filter(id=upload.id).update(
        uploaded=row[3].replace(tzinfo=timezone.utc))

    return upload


def import_package(row):
    try:
        package = Package.objects.get(name=row[0])
    except Package.DoesNotExist:
        package = Package()

    json = loads(row[2]) if row[2] else {}

    package.name = row[0]
    package.needs_sponsor = row[1]
    package.in_debian = json.get('in-debian', False)

    package.full_clean()
    package.save()

    return package


def import_users():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT email,'
            '    users.name,'
            '    lastlogin,'
            '    password,'
            '    type = 1,'
            '    verification,'
            '    ircnick,'
            '    jabber,'
            '    status,'
            '    user_countries.name,'
            '    gpg'
            '    FROM users'
            '    LEFT JOIN user_countries'
            '        ON (users.country_id = user_countries.id);'
        )

        for row in cursor.fetchall():
            try:
                user = update_user(row)
                update_profile(user, row)
                import_subscriptions(user)

                if row[10]:
                    update_gpg_key(user, row)
            except Exception as e:
                print(f'> Error importing user: {row[0]}\n> {e}')


def import_subscriptions(user):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT package,'
            '    level'
            '    FROM package_subscriptions'
            '    LEFT JOIN users'
            '        ON users.id = package_subscriptions.user_id'
            '    WHERE email = %s;',
            [user.email]
        )
        for row in cursor.fetchall():
            try:
                sub = PackageSubscription.objects.get(user=user, package=row[0])
            except PackageSubscription.DoesNotExist:
                sub = PackageSubscription()

            sub.package = row[0]
            sub.on_upload = True if row[1] == 1 else False
            sub.on_comment = True if row[1] == 2 else False
            sub.user = user

            sub.full_clean()
            sub.save()


def update_user(row):
    email = BaseUserManager.normalize_email(row[0])

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User()

    user.email = email
    user.name = row[1]
    user.last_login = row[2].replace(tzinfo=timezone.utc)
    user.date_joined = row[2].replace(tzinfo=timezone.utc)
    user.is_staff = row[4]
    user.is_superuser = row[4]
    user.is_active = True

    # md5 passwords
    if len(row[3]) == 32:
        user.password = f'md5$${row[3]}'
    # bcrypt passwords
    elif len(row[3]) == 60:
        user.password = f'bcrypt${row[3]}'
    else:
        user.password = '!disabled'

    # account not validated
    if row[5] is not None:
        user.password = '!tovalidate'

    user.full_clean()
    user.save()

    return user


def update_profile(user, row):
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile()

    profile.user = user

    if row[9]:
        profile.country = Countries.objects.get(name=row[9])

    profile.ircnick = row[6] if row[6] else ''
    profile.jabber = row[7] if row[7] else ''

    if row[8] == 2:
        profile.status = 3
    elif row[8] == 3:
        profile.status = 2
    else:
        profile.status = row[8]

    profile.full_clean()
    profile.save()


def update_gpg_key(user, row):
    gpg = GnuPG()

    try:
        key = Key.objects.get(user=user)
    except Key.DoesNotExist:
        key = Key()

    gpg.import_key(row[10])
    keyring = gpg.get_keys_data()[0]
    if len(gpg.get_keys_data()) > 1:
        raise ExceptionGnuPGMultipleKeys(
            'Multiple keys not supported')

    algo = keyring.get_algo()

    if algo not in ('1', '22'):
        raise Exception(f'Invalid algo: {algo}')

    algo = GPGAlgo.objects.get(gpg_algorithm_id=algo)
    size = keyring.get_size()

    if (algo.minimal_size_requirement
            and int(size) < algo.minimal_size_requirement
            and not (algo.name == 'rsa' and int(size) >= 2048)):
        raise Exception(f'Key too small: {size}')

    key.key = row[10]
    key.user = user
    key.size = size
    key.algorithm = algo
    key.fingerprint = keyring.fpr

    key.full_clean()
    key.save()

    key.update_subkeys()


def remove_duplicated_emails():
    print('Remove duplicated emails')

    with connection.cursor() as cursor:
        cursor.execute(
            'WITH dup_email AS'
            '    (SELECT MAX(id) AS id, email'
            '        FROM users'
            '        GROUP BY email'
            '        HAVING COUNT(email) > 1)'
            '    DELETE FROM users'
            '        WHERE'
            '                (id NOT IN'
            '                    (SELECT id'
            '                        FROM dup_email)'
            '            AND'
            '                email IN'
            '                    (SELECT email'
            '                        FROM dup_email));'
        )


def drop_spam_users():
    print('Drop spam users')

    with connection.cursor() as cursor:
        cursor.execute(
            'DELETE FROM users'
            '    WHERE length(name) > 64;'
        )


def add_missing_constraints():
    print('Add missing constraints')

    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE password_reset'
            '    DROP CONSTRAINT password_reset_user_id_fkey,'
            '    ADD CONSTRAINT password_reset_user_id_fkey'
            '        FOREIGN KEY (user_id)'
            '        REFERENCES users(id)'
            '        ON DELETE CASCADE;'
        )


def drop_unused_tables():
    print('Drop unused tables')

    unused_tables = (
        'user_upload_key',
    )

    with connection.cursor() as cursor:
        for table in unused_tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table};')


def import_package_binary(upload, desc):
    for name, description in [line.split(' - ', maxsplit=1) for line in
                              desc.splitlines()]:
        try:
            binary = BinaryPackage.objects.get(name=name, upload=upload)
        except BinaryPackage.DoesNotExist:
            binary = BinaryPackage()

        binary.name = name
        binary.description = description
        binary.upload = upload

        binary.full_clean()
        binary.save()


if __name__ == '__main__':
    main()
