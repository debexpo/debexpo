This file is for you to describe the debexpo application. Typically
you would include information such as the information below:

Installation and Setup
======================

setuptools way
--------------

Install ``debexpo`` using easy_install::

    easy_install debexpo

Make a config file as follows::

    paster make-config debexpo config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.

Debian way
----------

$ sudo apt-get install python-pylons python-babel
$ mkdir -p $HOME/lib/lib/python2.5/site-packages
$ export PYTHONPATH=$PYTHONPATH:$HOME/lib/lib/python2.5/site-packages
$ python setup.py develop --prefix=~/lib -N
$ paster make-config debexpo config.ini
$ vim config.ini
# fix at least the path "debexpo.repository = /tmp/debexpo_cache/"
$ paster setup-app config.ini
$ python setup.py compile_catalog
$ paster serve config.ini

And go to http://127.0.0.1:5000 with your browser.
