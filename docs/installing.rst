.. _installing:

=================================
Installing and setting up debexpo
=================================

debexpo is easy to set up on your own. Simply follow the instructions below.

There are two solutions:
 1. Install all dependencies on your system as root.
 2. Install dependencies and debexpo in an isolated environment using
    virtualenv.

Getting debexpo
---------------

You can clone the git repository::

    git clone https://salsa.debian.org/mentors.debian.net-team/debexpo.git

Dependencies needed for both methods
------------------------------------

Whatever method you choose, these packages are required::

    sudo apt-get install python3 iso-codes gnupg dpkg-dev
    debhelper redis-server devscripts lintian

While developing, you will need additional packages to run the test suite::

    sudo apt-get install cdbs

Installing on Debian as root
----------------------------

You need to install the required packages. Using `apt`, you should execute::

    sudo apt-get install python3-django python3-debian python3-celery
    python3-bcrypt python3-django-celery-beat python3-redis python3-django-redis
    python3-fakeredis python3-lupa python3-debianbts

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

Install python module `venv`::

    sudo apt install python3-venv

Debexpo installation
~~~~~~~~~~~~~~~~~~~~

First, create a new virtualenv for debexpo, and enter it::

   python3 -m venv venv
   source ./venv/bin/activate

ote that now, whenever you run "python", you run an interpreter that
is sandboxed to the "virtualenv" in question. You can test this by
typing::

    which python

and you will see it is not /usr/bin/python! You can now install debexpo. This
will download and install all required libraries::

    python setup.py develop

If for any reason you need to exit the virtualenv, you may enter
`deactivate` to exit the virtualenv.

Editing your configuration
--------------------------

Now edit `debexpo/settings/develop.py` to match your configuration.

Setting up the application
--------------------------

Execute the following commands to setup the application::

    python manage.py migrate

Running debexpo
---------------

Using django's built-in webserver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply execute::

    python manage.py runserver

and visit http://localhost:8000/ in your web browser.

Using Apache
~~~~~~~~~~~~

(Canonical instructions for getting Django apps working under Apache are
`here <https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/modwsgi/#using-mod-wsgi-daemon-mode>`_.)

#. Install `apache2` and `libapache2-mod-wsgi-py3`::

    sudo apt install apache2 libapache2-mod-wsgi-py3

#. Enable the module::

    sudo a2enmod wsgi-py3

#. Add the following to your site configuration::

    WSGIDaemonProcess example.com python-home=/path/to/venv python-path=/path/to/mysite.com
    WSGIProcessGroup example.com

    WSGIScriptAlias / /path/to/mysite.com/mysite/wsgi.py process-group=example.com

    Alias /robots.txt /path/to/mysite.com/static/robots.txt
    Alias /favicon.ico /path/to/mysite.com/static/favicon.ico

    Alias /media/ /path/to/mysite.com/media/
    Alias /static/ /path/to/mysite.com/static/

    <Directory /path/to/mysite.com/static>
        Require all granted
    </Directory>

    <Directory /path/to/mysite.com/media>
        Require all granted
    </Directory>

    WSGIScriptAlias / /path/to/mysite.com/mysite/wsgi.py

    <Directory /path/to/mysite.com/mysite>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
