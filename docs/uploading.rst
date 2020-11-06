.. _uploading:

=========
Uploading
=========

Uploading to debexpo
--------------------

Uploading to a debexpo repository is easy. You must use `dput
<http://packages.debian.org/dput>`_ as this is the only tool that can upload via
HTTP (at the time of writing).  (Former versions of debexpo used HTTP uploads
with authentication which repeatedly failed due to dput bugs which were in fact
urllib2 API changes.)

Setting up dput
~~~~~~~~~~~~~~~

Once you have debexpo and dput installed and set up, add an entry like the
following to your ``~/.dput.cf``::

    [debexpo]
    fqdn = localhost:8000
    incoming = /upload
    method = http
    allow_unsigned_uploads = 0

You may have to change the `fqdn` to suit your setup.

Uploading the package
~~~~~~~~~~~~~~~~~~~~~

Now you should execute::

    dput debexpo package_version_source.changes

You will get an output like this::

    % dput -f debexpo odccm_0.11.1-17_source.changes
    Uploading to debexpo (via http to localhost:8000): ...

At this point your upload will run and you should see the logs flying by
showing the status of the upload. The `*.changes` file will get uploaded last

Upload processing for debexpo
-----------------------------

A package in debexpo can be uploaded using two distinct methods:

Paths used:

**incoming queue**: config key ``debexpo.upload.incoming`` with ``/pub`` appened
**processing queue**: config key ``debexpo.upload.incoming``

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

Uploaded files are stored into the **incoming queue**.

Upload with FTP
~~~~~~~~~~~~~~~

A modified version of ``vsftpd`` runs on mentors, allowing anonymous uploads to
the root directory of the **incoming queue** (which is the same as the HTTP
queue).

**Note:**: FTP uploads are permitted under existing sub-directories, which
currently includes:

- ``./pub/``
- ``./pub/UploadQueue``

Processing of uploaded files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether files were uploaded using HTTP or FTP method, they are processed by
debexpo's ``importuploads`` cronjob.

Cleaning-up of stale files
``````````````````````````
Stall files older than 6 hours are cleanup automatically. This is true only for
files directly under the **incoming queue**.

Files located in sub-directories or in the **processing queue** are left
stalled.

Copying to the processing queue
```````````````````````````````

For every ``.changes`` files located in the following directories in the
**incoming queue**:

- ``.``
- ``./pub/UploadQueue``

Each referenced files (and the ``.changes``) are moved to the **processing
queue**

Currently, files located in any other sub-directories of the **incoming queue**
are ignored.

Running the importer on uploaded files
``````````````````````````````````````

The importer validates the upload and run various plugins around it.
In some cases, it can take resources from Debian archive or the **local
repository** and copy files in the **processing queue** to complete the upload.

Once all tests passed, files are copied over the **local repository** and the
importer returns to ``importuploads``.

If the importer fails, it will remove the ``.changes`` and all referenced files.

Cleaning-up the **processing queue**
````````````````````````````````````
Each files listed while copying to the **processing queue** are removed once the
importer has finished (regardless of its return status).
