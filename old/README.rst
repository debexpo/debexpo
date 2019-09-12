Installing and running debexpo
==============================

For installation instructions, see `<docs/installing.rst>`__

Running tests
=============

Hooray! Now you're ready to run the automated tests. (The code for the
tests lives in ``debexpo/tests/*``. This is a test suite; you can read
more about test suites `here`_.)

::

  % nosetests --with-pylons=test.ini

As of the time of writing, all the tests pass.

(Nosetests is a "test runner" package that provides some useful add-ons. It
has its own idiosyncracies, though.)

.. _here: http://en.wikipedia.org/wiki/Test_suite

Debugging a debexpo test that fails
===================================

So you've found a test that fails (F) or exits with an unhandled exception (E)?
Time to use the Python debugger.

Run the test suite with these parameters::

  % nosetests --with-pylons=test.ini --pdb-failures --pdb-errors

(If you've used ``pdb.set_trace()``, this is an automatic way that Nose gives
you that functionality.)

debexpo documentation
=====================

The debexpo documentation is written in `reStructuredText`_ and can be found
inside the ``docs/`` directory. You can find the current installation guide at
`<docs/installing.rst>`__. You can build and view the HTML docs locally by
executing::

  % sudo apt-get install python-sphinx # needed to build the docs
  % cd docs/
  % make html
  % sensible-browser .build/html/index.html

.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
