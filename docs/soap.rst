.. _soap:

==================
SOAP documentation
==================

debexpo repositories can be accessed by using SOAP using its `soap` controller.
Its methods are described below:

.. method:: uploader(email)

   Returns an array of packages given an uploader's email address.

   *email* is the email address you are querying.

.. method:: section(name)

   Returns an array of packages given a section name.

   *name* is the name of the section you are querying.

.. method:: maintainer(email)

   Returns an array of packages given a maintainer's email address.

   *email* is the email address you are querying.

.. method:: packages()

   Returns an array of all packages.

.. method:: package(name, version)

   Returns details on a specific package and version.

   *name* is the package name you are querying.

   *version* is the version name you are querying.

Example client
==============

Using SOAPpy::

    import SOAPpy
    server = SOAPpy.SOAPProxy("http://localhost:5000/soap")
    print server.section(name='utils')

And the output::

    <SOAPpy.Types.structType retval at 141282572>: {'stringArray': <SOAPpy.Types.structType stringArray at 141279660>: {'string': ['odccm', '0.11.1-17', 'Jonny Lamb <jonny@debian.org>', 'odccm - Daemon to keep a connection to Windows Mobile device', 'http://localhost:5000/package/odccm']}}
