.. _building:

=======================
Building the software
=======================

If you like to build the software you can get the Git repository from
https://salsa.debian.org/mentors.debian.net-team/debexpo using::

    git clone https://salsa.debian.org/mentors.debian.net-team/debexpo.git

Then simply enter into the debexpo directory and execute ``python3 setup.py
build``::

    cd debexpo
    python3 setup.py build

It is easier in some situations to leave debexpo in its source directory and
run it from there. However, if you wish to have it installed, create a
virtualenv environment::

    sudo apt install python3-venv
    python3 -m venv venv
    source ./venv/bin/activate

Then you can safely::

    python3 setup.py install

to install the package in your encapsulated environment.

If you attempt to install the package without virtualenv then setuptools (the
Python software management system) will install the files into the system-wide
directories ``/usr/lib/pythonX.Y/site-packages/``. Setuptools is not good at
removing files again and it is generally a bad idea to mix
setuptools-installed packages with Debian packages. So you should know what
you are doing.

