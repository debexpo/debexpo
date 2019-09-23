.. _contributing:

============
Contributing
============

Help is always welcome in debexpo. There are also a number of ways
to contribute:

* `Fixing bugs
  <https://salsa.debian.org/mentors.debian.net-team/debexpo/issues/>`_
* Testing the software and filing bugs
* Filing wishlist bugs
* Implementing new features
* Writing new plugins

Getting the source
==================

You can clone the Git repository using::

    git clone https://salsa.debian.org/mentors.debian.net-team/debexpo.git

Running tests
=============

`tox` is used to run tests. Install it with::

   sudo apt install tox

Then, run it::

   tox

This will run tests, coverage (available in ``htmlcov``) and flake8.

How we use branches
===================

Contributions to Debexpo should be based on the "live" branch.

We recommend rebasing your work so that it is based on the latest "origin/live"
just before you submit the changes for review.

The branch *live* indicates what is running on the main site.

Where to send patches
=====================

You should send patches either as `merge request
<https://salsa.debian.org/mentors.debian.net-team/debexpo/merge_requests>`_
(preferred) or directly via email to us.

Send any other feedback and information request to support@mentors.debian.net.

We also welcome Git branches.
