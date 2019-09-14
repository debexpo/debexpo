"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Project name and version
    name='debexpo',
    version='3.0.0',

    # Descriptions
    description='the software running behind mentors.debian.net',
    long_description=long_description,

    # Homepage for mentors
    url='https://mentors.debian.net',

    # Authors
    author='The Debexpo maintainers (see AUTHORS)',
    author_email='support@mentors.debian.net',

    # Related metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django :: 2.2',
    ],
    keywords='debian mentors packaging',

    # What packages to install
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'old']),

    # Python version requirements
    python_requires='>=3.7, <4',

    # Requirements
    install_requires=[
        'django==2.2.5'
    ],

    # Project urls
    project_urls={
        'Bug Reports': 'https://salsa.debian.org/mentors.debian.net-team/debexpo/issues',  # noqa: E501
        'Source': 'https://salsa.debian.org/mentors.debian.net-team/debexpo',
    },
)
