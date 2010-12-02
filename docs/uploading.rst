.. _uploading:

=========
Uploading
=========

Uploading to a debexpo repository is easy. You must use `dput <http://packages.debian.org/dput>`_
as this is the only tool that can upload via HTTP (at the time of writing).

Setting up dput
---------------

Once you have debexpo and dput installed and set up, add an entry like the following to
your ``~/.dput.cf``::

    [debexpo]
    fqdn = localhost:5000
    incoming = /upload/
    login = email@address.com
    method = http
    allow_unsigned_uploads = 0

You should change the `login` entry with your username, and you may have to change the `fqdn` to
suit your setup.

Uploading the package
---------------------

Now you should execute::

    dput debexpo package_version_source.changes

You will get an output like this::

    % dput -f debexpo2 odccm_0.11.1-17_source.changes
    Uploading to debexpo2 (via http to localhost:5000):
      odccm_0.11.1-17.dsc: need authentication.
        Password for debexpo:

At this point you should enter your password, and if you get it correct, your upload will run
and you should see the logs flying by showing the status of the upload.
