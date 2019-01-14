.. _installing:

=================================
Installing and setting up debexpo
=================================

debexpo is easy to set up on your own. Simply follow the instructions below.

There are two solutions:
 1. Install all dependencies on your system as root.
 2. Install dependencies and debexpo in an isolated environment using
    virtualenv and virtualenvwrapper.

Getting debexpo
---------------

You can clone the git repository::

    git clone https://salsa.debian.org/mentors.debian.net-team/debexpo.git

Dependencies needed for both methods
------------------------------------

Whatever method you choose, these packages are required::

    sudo apt-get install python-apt python-debian python-lxml iso-codes
    python-dulwich

If you want to run qa plugins, you will need `lintian` and
`dpkg-dev`::

    sudo apt-get install lintian dpkg-dev

Installing on Debian as root
----------------------------

You need to install the required packages. Using `apt`, you should execute::

    sudo apt-get install python-setuptools python-sphinx python-pylons python-sqlalchemy python-soappy python-nose python-pybabel

`python-nose` is optional if you don't want to run the test suite.


You also need `python-soaplib (version >= 0.8.2)`_.

Using pip::

    sudo pip install soaplib

.. _`python-soaplib (version >= 0.8.2)`: http://pypi.python.org/pypi/soaplib

Installing in a virtualenv
--------------------------

Using this method, you will create a virtual Python environment in
which you can install the dependencies for debexpo without altering your
system (i.e., without requiring root). In addition, this will also let
you isolate debexpo's requirements, in the event an application installed
globally might require a conflicting version of a library, or vice versa.

Virtualenv setup
~~~~~~~~~~~~~~~~

Skip this section if you already have a working virtualenv setup.

Install `virtualenvwrapper`::

    sudo apt-get install virtualenvwrapper

Debexpo installation
~~~~~~~~~~~~~~~~~~~~

First, create a new virtualenv for debexpo, and enter it::

    mkvirtualenv --system-site-packages expo
    workon expo

*Note*: If you get a "command not found" error for "mkvirtualenv", run
the following in your shell::

    . /etc/bash_completion.d/virtualenvwrapper

Note that now, whenever you run "python", you run an interpreter that
is sandboxed to the "virtualenv" in question. You can test this by
typing::

    which python

and you will see it is not /usr/bin/python! Additionally, your shell prompt
should have a little prefix before the prompt that looks like::

    (expo)

You can now install debexpo. This will download and install all
required libraries::

    python setup.py develop

If for any reason you need to exit the virtualenv, you may enter
`deactivate` to exit the virtualenv.

Editing your configuration
--------------------------

Now edit `development.ini` to match your configuration.

Setting up the application
--------------------------

Execute the following commands to setup the application::

    paster setup-app development.ini
    python setup.py compile_catalog

Running debexpo
---------------

Using paste's built-in webserver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply execute::

    paster serve development.ini

and visit http://localhost:5000/ in your web browser.

Using Apache
~~~~~~~~~~~~

(Canonical instructions for getting Pylons apps working under Apache are
`here <http://wiki.pylonshq.com/display/pylonsdocs/Running+Pylons+apps+with+Webservers>`_.)

#. Install `apache2`, `mod-fastcgi` and `flup`::

    sudo apt-get install python-flup apache2 libapache2-mod-fastcgi

#. Edit the ``server:main`` section of your `debexpo.ini` so it reads
   something like this::

    [server:main]
    use = egg:PasteScript#flup_fcgi_thread
    host = 0.0.0.0
    port = 6500

#. Add the following to your config::

    <IfModule mod_fastcgi.c>
      FastCgiIpcDir /tmp
      FastCgiExternalServer /some/path/to/debexpo.fcgi -host localhost:6500
    </IfModule>

  Note: Parts of this may conflict with your `/etc/apache2/conf-available/fastcgi.conf`.
  `/some/path/to/debexpo/fcgi` need not physically exist on the webserver.
