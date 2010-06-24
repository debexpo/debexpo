# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('%s uploaded to %s' % (c.package, c.config['debexpo.sitename'])) }

${ _('Hi.') }

${ _('''Your upload of the package '%s' to %s was
successful. Others can now see it. The URL of your package is:''' %
(c.package, c.config['debexpo.sitename'])) }
${ c.config['debexpo.server'] }${ h.url('package', packagename=c.package) }

${ _('''The respective dsc file can be found at:''') }
${ c.dsc_url }

% if c.config['debexpo.debian_specific'] == 'true':
${ _('''If you do not yet have a sponsor for your package you may want to go to
%s
and set the "Seeking a sponsor" option to highlight your package on the
welcome page.''' % c.rfs_url) }

${ _('''You can also send an RFS (request for sponsorship) to the debian-mentors
mailing list. Your package page will give your suggestions on how to
send that mail.''') }

${ _('''Good luck in finding a sponsor!''') }
% endif

${ _('Thanks,') }
