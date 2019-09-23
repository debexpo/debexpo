# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('Failure in importer') }

${ _('''Hello,

There was a failure in importing a package into debexpo. The problem
appears to be debexpo itself. The error message was:''') }

${ c.message }

${ _('This message can be found in the logs.') }

${ _('Thanks,') }
