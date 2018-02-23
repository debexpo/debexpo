.. _installing:

=================================
Installing and setting up debexpo
=================================

debexpo is easy to set up on your own. Simply follow the instructions below.

Installing on Debian Lenny:
---------------------------

You need to install the required packages. Using apt, you should execute::

    sudo aptitude install python-setuptools python-apt python-sphinx python-pylons python-debian python-sqlalchemy lintian dpkg-dev python-nose python-pybabel

`lintian` and `dpkg-dev` are optional if you do not want to run any plugins,
and `python-nose` is optional if you don't want to run the test suite.

Getting debexpo
---------------

You can either download a release tarball, or clone from the Git repository.

`The debexpo website <http://debexpo.workaround.org/>`_ will contain details
about releases.

Or you can clone the repository contents by executing::

    git clone git://debexpo.workaround.org/debexpo.git

Editing your configuration
---------------------------

Create a configuration file::

    paster make-config debexpo debexpo.ini

Next you should edit the default configuration file ``debexpo.ini``.
You should only have to look at options with the ``DEBEXPO``
comment preceeding them. You can find explanations of the `debexpo.*` options
on the :ref:`config-file` page.

If you just want to get it running somehow, edit at least the path
``debexpo.repository = /tmp/debexpo_cache/``.

Setting up the application
--------------------------

Execute the following commands to setup the application::

    paster setup-app debexpo.ini
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

