.. _writing-cronjobs:

================
Writing cronjobs
================

Writing cronjobs works similar to plugins. The invokation and arguments
passed are different though.
A minimal cronjob looks like this::

    from debexpo.cronjobs import BaseCronjob

    class ImportUpload(BaseCronjob):
        def setup(self):
            pass

        def teardown(self):
            pass

        def deploy(self):
            self.log.debug("Hello World")

    cronjob = ImportUpload
    schedule = 5


The architecture
================

A cronjob should be subclassed from BaseCronjob. That ensure API compliant
invokation. A worker thread runs your jobs cyclically, persistence is guaranteed
for the object runtime. Technically, you ``must`` define two objects in your
module.

Invokation::
    cronjob = ImportUpload
    schedule = 5

The 'cronjob' attribute is an object reference which should be instantiated upon
cronjob invokation. The 'schedule' attribute defines how often your cronjob should
invoke your worker method. This must be an integer and has to be interpreted as
n-th iteration. For example, setting this to 5 means, the Worker thread will
execute your `deploy` method every 5th iteration. This is a pure abstract counter
clock, the actual delay is determined by cronjob runtime and setting of the
`debexpo.cronjob_delay` variable in your ini file.

The constructor
===============

Please don't override the base class constructor, it will call your `setup` method
if you need any setup. The following attributes will be instantiated for your
cronjob:

``self.parent``
--------------

This is a reference to the worker object, which instantiated your cronjob. You can
call any method in from there, if necessary.

``self.config``
--------------

This is an instantiated configuration object. You can access every Debexpo
configuration setting from it.

``self.log``
--------------

An instantiated log object, use it to display messages within the worker thread

The destructor
==============

Similarly to the constructor, don't override the destructor. Use the `teardown`
method instead

The worker method invokation
============================

Implement the `deploy` method as your working horse. It will be called regularly
and run your stuff. The Worker is designed as single threaded application, which
means your method will block the entire cron job architecture. Don't do anything
which shall not be run synchronously.

