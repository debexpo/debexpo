# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('%s package has been removed from %s' % (c.package, c.config['debexpo.sitetitle'])) }

${ _('Your package %s %s has been removed from %s for the following reason:' % (c.package, c.version, c.config['debexpo.sitename'])) }

${ c.reason }

${ _('Thanks,') }
