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
        "Pylons>=1.0",
        "SQLAlchemy>=0.6",
        "Webhelpers>=0.6.1",
        "Babel>=0.9.6",
        "ZSI",
        "python-debian==0.1.16",
        "soaplib==0.8.1"],
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
    debexpo-importer = debexpo.scripts.debexpo_importer:main
    """,
)
