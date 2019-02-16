==================
Database migration
==================

Before taking any action on the database, **make sure you have a working
backup**.

Requirements
============

The migration process is achieve through alembic scripts. Make sure you have it
installed:

With system-wide installation::

   apt install python-alembic

With virtualenv installation::

   python setup.py develop

Schema migration
================

Make your backups.

The next two commands inform you of the list of revision and where the current
database is at::

   alembic -c development.ini history
   alembic -c development.ini current

Start the migration with::

   alembic -c development.ini upgrade head

Downgrading
===========

You can downgrade by following the exact same procedure as the `Schema
migration` and replacing last command by::

   alembic -c development.ini downgrade REVISION

Creating new migration scripts
==============================

To create new migration script, just run::

   alembic -c development.ini revision \
   -m "Description of the schema modification"

Then edit the file created.

Read carefully alembic documentation as each one of the database engines brings
new constraints (See `SQlite ALTER TABLE
<https://www.sqlitetutorial.net/sqlite-alter-table/>`_).

`Alembic documentation <https://alembic.sqlalchemy.org/en/latest/>`_
