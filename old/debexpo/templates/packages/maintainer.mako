# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Packages maintained by %s') % c.maintainer }</h1>

<%include file="list.mako" />
