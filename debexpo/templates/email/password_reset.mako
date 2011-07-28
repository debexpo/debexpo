# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: ${ _('You requested a password reset') }

${ _('''Hello,

You can reset your password by clicking on the link below. If you did
not request a password reset, then you can ignore this.''') }

${ c.password_reset_url }

${ _('Thanks,') }
