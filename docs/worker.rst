.. _worker:

====================
Using debexpo worker
====================

debexpo has a few tasks that need running periodically or on specific trigger.
Examples of tasks are:

- periodical
  * upload import
  * package cleanup
  * account cleanup
- on trigger
  * repository update

This chapter explains how to run those tasks.

Run the worker
--------------

To run the worker, execute celery::

    celery --app debexpo worker --beat

List tasks
----------

To get a list of tasks currently registered in the worker, run::

    celery --app debexpo inspect registered

Run a task on demand
--------------------

You may need sometime to run a task immediately. To do so, run::

    celery --app debexpo call debexpo.importer.tasks.importer

Replace the last argument by the name of your task.
