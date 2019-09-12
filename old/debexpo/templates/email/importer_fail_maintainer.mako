# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('Failed to import %s') % c.package }

${ _('''Hello,

There was a failure in importing your package "%s" into
the repository. The problem appears to be in the repository software
and not your package.

Sorry for the inconvenience. The administrator has been notified.
Please try again soon.''') % c.package }

${ _('Thanks,') }
