.. _config-file:

==================
Configuration file
==================

The configuration file for debexpo is found under
``debexpo/settings/debexpo.py``. This file is a link that you must change
according to your environment. By default, it points to ``develop.py`` that is
suitable for development purposes.

All configuration files must include the ``common.py`` that define base
settings for all environment.

The following example demonstrate how to create a configuration file for a new
environment::

   cd debexpo/settings
   # Use prod.py as a starting point
   cp prod.py live.py
   # Edit live.py according to your needs
   # then, make it use by debexpo
   ln -sf live.py debexpo.py

Django Settings
---------------

Django settings are documented in the online `Django reference`_

Debexpo Settings
----------------

.. _Django reference: https://docs.djangoproject.com/en/2.2/ref/settings/
