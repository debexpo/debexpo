# Generated by Django 2.2.5 on 2019-11-27 15:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

DISTRIBUTIONS = (
    ('bullseye', 'Debian'),
    ('bullseye-backports', 'Debian Backports'),
    ('bullseye-backports-sloppy', 'Debian Backports'),
    ('bullseye-security', 'Debian'),
    ('bullseye-updates', 'Debian'),
    ('buster', 'Debian'),
    ('buster-backports', 'Debian Backports'),
    ('buster-backports-sloppy', 'Debian Backports'),
    ('buster-security', 'Debian'),
    ('buster-updates', 'Debian'),
    ('experimental', 'Debian'),
    ('jessie', 'Debian'),
    ('jessie-backports', 'Debian Backports'),
    ('jessie-backports-sloppy', 'Debian Backports'),
    ('jessie-security', 'Debian'),
    ('jessie-updates', 'Debian'),
    ('oldstable', 'Debian'),
    ('oldstable-backports', 'Debian Backports'),
    ('oldstable-backports-sloppy', 'Debian Backports'),
    ('oldstable-proposed-updates', 'Debian'),
    ('oldstable-security', 'Debian'),
    ('sid', 'Debian'),
    ('squeeze', 'Debian'),
    ('squeeze-backports', 'Debian Backports'),
    ('squeeze-backports-sloppy', 'Debian Backports'),
    ('squeeze-security', 'Debian'),
    ('squeeze-updates', 'Debian'),
    ('stable', 'Debian'),
    ('stable-backports', 'Debian Backports'),
    ('stable-proposed-updates', 'Debian'),
    ('stable-security', 'Debian'),
    ('stretch', 'Debian'),
    ('stretch-backports', 'Debian Backports'),
    ('stretch-backports-sloppy', 'Debian Backports'),
    ('stretch-security', 'Debian'),
    ('stretch-updates', 'Debian'),
    ('testing', 'Debian'),
    ('testing-proposed-updates', 'Debian'),
    ('testing-security', 'Debian'),
    ('UNRELEASED', 'Debian'),
    ('unstable', 'Debian'),
    ('wheezy', 'Debian'),
    ('wheezy-backports', 'Debian Backports'),
    ('wheezy-backports-sloppy', 'Debian Backports'),
    ('wheezy-security', 'Debian'),
    ('wheezy-updates', 'Debian'),
)


def create_distributions(apps, schema_editor):
    Distribution = apps.get_model('packages', 'Distribution')
    Project = apps.get_model('packages', 'Project')

    for name, project in DISTRIBUTIONS:
        project, _ = Project.objects.get_or_create(name=project)
        distribution = Distribution()
        distribution.name = name
        distribution.project = project

        distribution.full_clean()
        distribution.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name',
                                          unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name',
                                          unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name',
                                          unique=True)),
                ('needs_sponsor', models.BooleanField(
                    default=False, verbose_name='Needs a sponsor?')),
                ('in_debian', models.BooleanField(
                    default=False, verbose_name='In Debian?')),
            ],
        ),
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name',
                                          unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name',
                                          unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name',
                                          unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PackageUpload',
            options={'ordering': ['-uploaded']},
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('version', models.CharField(max_length=100,
                                             verbose_name='Version')),
                ('changes', models.TextField(verbose_name='Changes')),
                ('closes', models.TextField(verbose_name='Closes bugs',
                                            blank=True)),
                ('git_ref', models.TextField(verbose_name='Git storage ref',
                                             blank=True, null=True)),
                ('uploaded', models.DateTimeField(
                    auto_now_add=True, verbose_name='Upload date')),
                ('component', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='packages.Component'
                )),
                ('distribution', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='packages.Distribution'
                )),
                ('package', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='packages.Package'
                )),
                ('uploader', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
        migrations.AddField(
            model_name='distribution',
            name='project',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='packages.Project'),
        ),
        migrations.CreateModel(
            name='SourcePackage',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('maintainer', models.CharField(
                    max_length=120, verbose_name='Maintainer')),
                ('homepage', models.TextField(null=True,
                                              blank=True,
                                              verbose_name='Homepage')),
                ('vcs', models.TextField(null=True, blank=True,
                                         verbose_name='VCS')),
                ('priority',
                 models.ForeignKey(null=True,
                                   blank=True,
                                   on_delete=django.db.models.deletion.SET_NULL,
                                   to='packages.Priority')),
                ('section',
                 models.ForeignKey(null=True,
                                   blank=True,
                                   on_delete=django.db.models.deletion.SET_NULL,
                                   to='packages.Section')),
                ('upload', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='packages.PackageUpload'
                )),
            ],
        ),
        migrations.CreateModel(
            name='BinaryPackage',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('homepage', models.TextField(null=True,
                                              blank=True,
                                              verbose_name='Homepage')),
                ('priority',
                 models.ForeignKey(null=True,
                                   blank=True,
                                   on_delete=django.db.models.deletion.SET_NULL,
                                   to='packages.Priority')),
                ('section',
                 models.ForeignKey(null=True,
                                   blank=True,
                                   on_delete=django.db.models.deletion.SET_NULL,
                                   to='packages.Section')),
                ('upload', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='packages.PackageUpload'
                )),
            ],
        ),
        migrations.RunPython(create_distributions),
    ]
