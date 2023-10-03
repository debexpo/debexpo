"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import sys
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as build
from os import path, system
from glob import glob

here = path.abspath(path.dirname(__file__))
sys.path.insert(0, here)

from project import PROJECT, VERSION, AUTHOR  # noqa: E402


class GenerateDjangoTranslation(build):
    def run(self):
        # Generate translations
        for source in glob('debexpo/**/*.po', recursive=True):
            system('msgfmt -c {} -o {}'.format(source,
                                               source.replace('.po', '.mo')))

        super().run()


# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Project name and version
    name=PROJECT,
    version=VERSION,

    # Descriptions
    description='the software running behind mentors.debian.net',
    long_description=long_description,

    # Homepage for mentors
    url='https://mentors.debian.net',

    # Authors
    author=AUTHOR,
    author_email='support@mentors.debian.net',

    # Related metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django :: 3.2',
    ],
    keywords='debian mentors packaging',

    # Hooks for setup
    cmdclass={
        'build_py': GenerateDjangoTranslation,
        'build_ext': GenerateDjangoTranslation,
    },

    # What packages to install
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'old']),
    data_files=[('.', ['project.py'])],
    package_data={'': [
        'debexpo/locale/*/*/*.mo',
        'debexpo/*/locale/*/*/*.mo'
    ]},

    # Python version requirements
    python_requires='>=3.11, <4',

    # Requirements
    install_requires=[
        'django >= 3.2.19, < 5',
        'bcrypt >= 3.2.2, < 4',
        'python-debian >= 0.1.49, < 1',
        'celery >= 5.2.6, < 6',
        'django-celery-beat >= 2.4.0, < 3',
        'redis >= 4.3.4, < 5',
        'django-redis >= 5.2.0, < 6',
        'python-debianbts >= 4.0.1, < 5',
        'lxml >= 4.9.2, < 5',
        'dulwich >= 0.21.2, < 1',
        'djangorestframework >= 3.14.0, < 4',
        'django-filter >= 23.1, < 24',
        'drf-extensions >= 0.7.1, < 1',
        'distro-info >= 1.0, < 2'
    ],

    extras_require={
        'testing': [
            'fakeredis >= 1.9.0, < 2',
            'lupa >= 1.14.1, < 2',
        ],
    },

    # Project urls
    project_urls={
        'Bug Reports': 'https://salsa.debian.org/mentors.debian.net-team/debexpo/issues',  # noqa: E501
        'Source': 'https://salsa.debian.org/mentors.debian.net-team/debexpo',
    },
)
