.. _uploading:

=========
Uploading
=========

Uploading to debexpo
--------------------

Uploading to a debexpo repository is easy. You must use `dput <http://packages.debian.org/dput>`_
as this is the only tool that can upload via HTTP (at the time of writing).
(Former versions of debexpo used HTTP uploads with authentication which repeatedly
failed due to dput bugs which were in fact urllib2 API changes.)

Setting up dput
~~~~~~~~~~~~~~~

Once you have debexpo and dput installed and set up, add an entry like the following to
your ``~/.dput.cf``::

    [debexpo]
    fqdn = localhost:5000
    incoming = /upload/email@address/yourpassword
    method = http
    allow_unsigned_uploads = 0

You should change the `email@address` and `yourpassword` entries with the email address and
password you use to login. And you may have to change the `fqdn` to suit your setup.

Uploading the package
~~~~~~~~~~~~~~~~~~~~~

Now you should execute::

    dput debexpo package_version_source.changes

You will get an output like this::

    % dput -f debexpo odccm_0.11.1-17_source.changes
    Uploading to debexpo (via http to localhost:5000): ...

At this point your upload will run and you should see the logs flying by
showing the status of the upload. The `*.changes` file will get uploaded last

Upload processing on mentors.debian.net
---------------------------------------

A package in debexpo can be uploaded using two distinct methods:

Upload with HTTP
~~~~~~~~~~~~~~~~

Files can be upload to the ``/upload`` route using the PUT HTTP verb.
Once the `.changes` has been uploaded, overwriting files it references is not
longer possible.

This security mechanism prevent messing with already uploaded packages while
allowing resuming interrupted transfers.

In the HTTP upload, only the following extensions are permitted:

- ``.asc``
- ``.buildinfo``
- ``.changes``
- ``.deb``
- ``.diff.gz``
- ``.dsc``
- ``.udeb``

Uploaded files are stored into the *incoming* queue
(``/var/cache/debexpo/incoming/pub`` on mentors).

Stall files older than 6 hours are cleaned-up by the cronjob ``importuploads``.
