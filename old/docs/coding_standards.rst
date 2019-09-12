.. _coding-standards:

================
Coding standards
================

Parts of this document are copied from `netconf's coding standards <http://git.debian.org/?p=netconf/netconf.git;a=blob;f=doc/coding_standards.txt;hb=HEAD>`_.

Python
======

* Python code adheres to `PEP-8 coding guidelines <http://www.python.org/dev/peps/pep-0008/>`_.

* Write all code for Python 2.5; thus, all features up until and including Python 2.5 may be used.

* If the choice is between a Python 2.5 way of implementing something, and a pre-2.5 way, the former should be taken.

* Existing pre-2.5 constructs which have been deprecated by Python 2.5 must be reimplemented accordingly.

* Existing pre-2.5 constructs which can merely be expressed more concisely with Python 2.5 can be migrated, and probably should be.

* Use the ``docs/py.template`` file as a start to all Python files. Alter author and copyright information if needed.

* Use Python unicode strings -- ``u'foo'`` instead of ``'foo'``.

* Private Python functions' names should start with an underscore.

General
=======

* Use UTF-8 everywhere.

* Limit line width to 100 characters.

* Everything is in English (including comments, variable names, etc.)

* All text that will be shown to users **must** be localized `using the Pylons framework <http://wiki.pylonshq.com/display/pylonsdocs/Internationalization+and+Localization>`_

* `Create tests <http://wiki.pylonshq.com/display/pylonsdocs/Unit+Testing>`_ using the Pylons framework for all functions or features that it is feasible for

* When showing potentially long lists of things use the `paginate` module.

* Use the `logging` module to log activity, and use the three severity levels.

Directory structure
===================

* Functions that deal with the database models should go into ``model/``.

* Functions that provide general functionality go into ``lib/helpers/``.

Mako Templates
==============

* Start all templates with ``# -*- coding: utf-8 -*-`` on the first line.

* Use correct, `validated <http://validator.w3.org/>`_, XHTML.

* Try to use the webhelpers where possible.

* Indent XHTML properly -- 4 spaces per level, as in the Python code.
