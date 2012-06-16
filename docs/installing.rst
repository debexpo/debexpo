.. _installing:

=================================
Installing and setting up debexpo
=================================

debexpo is easy to set up on your own. Simply follow the instructions below.

There are two solutions:
 1. install all dependencies on your system as root
 2. install dependencies and debexpo in an isolated environment using
    virtualenv

Getting debexpo
---------------

You can clone the git repository::

  git clone git://git.debian.org/debexpo/debexpo.git

You should use the 'devel' branch::
  git checkout devel

Dependencies needed for both methods
------------------------------------

Whatever method you choose, these packages are required::
  sudo apt-get install python-apt python-debian iso-codes

If you want to run qa plugins, you will need `lintian` and
`dpkg-dev`::
  sudo apt-get install lintian dpkg-dev

Installing on Debian Squeeze or Wheezy as root
---------------------------------------------------

You need to install the required packages. Using apt, you should execute::

    sudo apt-get install python-setuptools python-sphinx python-pylons python-sqlalchemy python-soappy python-nose python-pybabel

`python-nose` is optional if you don't want to run the test suite.


You also need python-soaplib version >= 0.8.2 :
http://pypi.python.org/pypi/soaplib

Using pip::
  sudo pip install soaplib


Installing in an virtualenv
---------------------------

Using this method, you will create a virtual Python environment in
which you can install dependencies for debexpo without altering your
system (i.e., without requiring root). In addition, this will also let
you isolate debexpo's requirements, in the event an application installed
globally might require a conflicting version of a library, or vise versa.

Virtualenv setup
~~~~~~~~~~~~~~~~

Skip this section if you already have a working virtualenv setup.

Install virtualenvwrapper::
  sudo apt-get install virtualenvwrapper

Dependencies
~~~~~~~~~~~~

To install lxml from sources, you will need `gcc`, `libxml2`,
`libxslt1.1` and `python-dev` ::
  sudo apt-get install gcc libxml2 libxml2-dev libxslt1.1 libxslt1-dev python-dev

Debexpo installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, create a new virtualenv for debexpo, and enter it::
  mkvirtualenv expo
  workon expo

You can now install debexpo. This will download and install all
required libraries::
  python setup.py develop

If for any reason you need to exit the virtualenv, you may enter
`deactivate` to exit the virtualenv.

Editing your configuration
---------------------------

Now edit `development.ini` to match your configuration.

Setting up the application
--------------------------

Execute the following commands to setup the application::

    paster setup-app development.ini
    python setup.py compile_catalog

Running debexpo
---------------

Using paste's built-in webserver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Simply execute::

    paster serve debexpo.ini

and visit http://localhost:5000/ in your web browser.

Using Apache
^^^^^^^^^^^^

(Canonical instructions for getting Pylons apps working under Apache are
`here <http://wiki.pylonshq.com/display/pylonsdocs/Running+Pylons+apps+with+Webservers>`_.)

#. Install apache2, mod-fastcgi and flup::

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
