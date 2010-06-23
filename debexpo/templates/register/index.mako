# -*- coding: utf-8 -*-

<%inherit file="../base.mako"/>

<h1>${ _('Sign up for your own account at %s') % c.config['debexpo.sitename'] }</h1>

  <p>
    ${ _('What type of account would you like to apply for?') }
  </p>

  <h2><a href="${ h.url.current(action='maintainer') }">${ _('Package Maintainer') }</a></h2>

  <p>
    ${ _('''A package maintainer is a person who takes care of Debian packages.
    If you create Debian packages from certain pieces of (so called
    "upstream") software then you are a maintainer. You do not need to be
    an official Debian Developer (DD) or Debian Maintainer (DM).''') }
  </p>

  <h2><a href="${ h.url.current(action='sponsor') }">${ _('Sponsor') }</a></h2>

  <p>
    ${ _('''Uploading new packages into Debian is only possible if you
    are a Debian Developer (DD) or Debian Maintainer (DM). If you want
    to help package maintainers to get their packages into Debian you
    can be a sponsor and check and upload packages on their behalf.''')}
  </p>
