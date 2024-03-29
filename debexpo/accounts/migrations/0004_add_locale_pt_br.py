# Generated by Django 3.2.15 on 2022-11-21 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='language',
            field=models.CharField(blank=True, choices=[
                ('en', 'English'),
                ('fr', 'French'),
                ('pt-br', 'Portuguese (Brazil)')
            ], max_length=100, verbose_name='Language'),
        ),
    ]
