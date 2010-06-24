# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Packages uploaded by %s') % c.username }</h1>

<p><a href="${ h.url('ppa', email=c.email) }">${ _('''View this uploader's personal package archive''') }</a></p>

<%include file="list.mako" />
