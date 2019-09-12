Debexpo
=======

debexpo is the software running behind https://mentors.debian.net.

It allows contributors to debian packaging to propose new software for inclusion
into `Debian`_.

The source is available from:

https://salsa.debian.org/mentors.debian.net-team/debexpo

Licensing and authors
---------------------

debexpo is released under the MIT license available in the `<COPYRIGHT>`__ file.

Current and former contributors are listed into the `<AUTHORS>`__ file.

Documentation
-------------

The debexpo documentation is written in `reStructuredText`_ and can be found
inside the ``docs/`` directory. You can find the current installation guide at
`<docs/installing.rst>`__. You can build and view the HTML docs locally by
executing::

  % sudo apt install python3-sphinx # needed to build the docs
  % cd docs/
  % make html
  % sensible-browser _build/html/index.html

Installing
----------

Installation documentation is available in `<docs/installing.rst>`__.

Contributing
------------

Report a bug
~~~~~~~~~~~~

To report a bug to debexpo, please fill-in an issue at this URL:

https://salsa.debian.org/mentors.debian.net-team/debexpo/issues

Include as much information as you can. We must be able to reproduce the crash
in order to fix it.

Contribute to debexpo
~~~~~~~~~~~~~~~~~~~~~

If you have enough knowledge (or willingness to learn) python, django and
debian packaging, you can help hacking debexpo code to add new feature or fix
bugs reported on the `issue tracker`_.

The current workflow for contributing is:

- Fork debexpo project to your personal workspace
- Work on a dedicated branch. (you can prefix your branch by fix/, feature/,
  doc/)
- When the hack is ready AND covered by tests, create a new merge request
  against the ``live`` branch for us to review.

We do ask that any code added/modified is covered by tests before merging.

Don't hesitate to join us on IRC (detail below).

Contact
-------

You can reach us by email using the address `support@mentors.debian.net`_.

For any question, we also are available on the IRC channel `#debexpo`_ from the
`OFTC`_ network.

.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
.. _#debexpo: https://webchat.oftc.net/?channels=%23debexpo
.. _OFTC: https://www.oftc.net
.. _Debian: https://www.debian.org
.. _support@mentors.debian.net: mailto:support@mentors.debian.net
.. _issue tracker: https://salsa.debian.org/mentors.debian.net-team/debexpo/issues
