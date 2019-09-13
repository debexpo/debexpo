.. debexpo documentation master file, created by sphinx-quickstart on Sun Jun  1 15:36:31 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to debexpo's documentation
===================================

debexpo (Debian package exposition) is a web application that allows you to
run a user-friendly public Debian package repository with social interaction
that you may be used to from social networking sites. debexpo is the basis for
the mentors.debian.net site but may be useful for others as well. It is
basically a Pylons application that can be deployed on any server. You do
not need anything more than Pylons, a little harddisk space and a database
like PostgreSQL, MySQL or Sqlite.

Setting up debexpo
------------------

.. toctree::
    :maxdepth: 1

    installing
    config_file

Using debexpo
-------------

.. toctree::
    :maxdepth: 1

    uploading
    plugins
    db_migration

Development documentation
-------------------------

.. toctree::
    :maxdepth: 1

    building
    writing_plugins
    writing_cronjobs
    coding_standards
    contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
