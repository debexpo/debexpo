# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<%include file="/user.mako"/>

<h1>${ _('Packages uploaded by %s') % c.profile.name }</h1>

<%include file="list.mako" />
