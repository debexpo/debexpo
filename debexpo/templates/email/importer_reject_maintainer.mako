# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('Package %s was rejected') % c.package }

${ _('''Hello,

Unfortunately your package "%s" was rejected because of the following
reason:''') % c.package }

${ c.message }

${ _('Please try to fix it and re-upload. Thanks,') }
