try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='debexpo',
    version="",
    description='the software running behind mentors.debian.net',
    author='The Debexpo developers',
    author_email='support@mentors.debian.net',
    url='https://mentors.debian.net',
    install_requires=[
        "Pylons>=1.0.2",
        "sphinx",  # for make build
        "SQLAlchemy>=0.6",
        "alembic>=1.0.0",
        "Webhelpers>=0.6.1",
        "Babel>=0.9.4",
        "python-debian>=0.1.16",
        "python-apt",
        "SOAPpy",                # client
        "dulwich",
        "nose>=1.3.7",           # ensure in virtualenv
        "passlib>=1.7.0",
        "bcrypt>=3.1.2",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'debexpo': ['i18n/*/LC_MESSAGES/*.mo']},
    message_extractors={'debexpo': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = debexpo.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [console_scripts]
    debexpo-importer = debexpo.bin.debexpo_importer:main
    debexpo-worker = debexpo.bin.debexpo_worker
    debexpo-user-importer = debexpo.bin.user_importer:main

    [nose.plugins]
    pylons = pylons.test:PylonsPlugin
    """,
)
