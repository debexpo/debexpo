.. _building:

=======================
Building the software
=======================

If you like to build the software you can get the Git repository from
`debexpo.workaround.org <http://debexpo.workaround.org/>`_ using::

    git clone git://debexpo.workaround.org/debexpo.git

Then simply enter into the debexpo directory and execute ``make build``::

    cd debexpo
    make build

It is easier in some situations to leave debexpo in its source directory and
run it from there. However, if you wish to have it installed, create a
virtualenv environment::

    aptitude install python-virtualenv
    virtualenv .
    source bin/activate

Then you can safely::

    make install

to install the package in your encapsulated environment.

If you attempt to install the package without virtualenv then setuptools (the
Python software management system) will install the files into the system-wide
directories ``/usr/lib/pythonX.Y/site-packages/``. Setuptools is not good at
removing files again and it is generally a bad idea to mix
setuptools-installed packages with Debian packages. So you should know what
you are doing.

