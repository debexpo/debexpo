# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('New %s package uploaded' % c.package) }

${ _('%s %s has been uploaded to the archive by %s.' % (c.package, c.version, c.user.name)) }

${ _('You can view information on the package by visiting:') }

${ c.config['debexpo.server'] }/${ h.url('package', packagename=c.package) }

${ _('You can change your subscription by visiting your user account settings.') }

${ _('Thanks,') }
