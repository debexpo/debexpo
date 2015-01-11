try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='debexpo',
    version="",
    #description='',
    #author='',
    #author_email='',
    #url='',
    install_requires=[
        "webob==1.0.8",
        "Pylons==1.0",
        "SQLAlchemy>=0.6",
        "Webhelpers>=0.6.1",
        "Babel>=0.9.4",
        "python-debian>=0.1.16",
        "apt>=0.7.8",
        "soaplib>=0.12",         # server
        "SOAPpy",                # client
        "chardet",
        "dulwich",
        "nose>=1.3.4",           # ensure in virtualenv
        ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'debexpo': ['i18n/*/LC_MESSAGES/*.mo']},
    message_extractors = {'debexpo': [
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
