# -*- coding: utf-8 -*-

<%inherit file="../base.mako"/>

% if c.user is not None:

    <h1>${ _('User activated') }</h1>

    <p>
      ${ _('Your account has been activated.') }
      ${ _('You can now %sproceed to login%s.') % ('<a href="' + h.url('my') + '">', '</a>') }
    </p>

% else:

    <h1>${ _('Invalid verification key') }</h1>

    <p>
      ${ _('The verification key you entered has not been recognised. Please try again.') }
    </p>

% endif
