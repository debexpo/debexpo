# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Subscribe to package %s') % c.package.name }</h1>

${ h.html.tags.form(h.url_for()) }
<p>${ h.html.tags.select('level', c.current_subscription, c.subscriptions) }
<br/>
${ h.html.tags.submit('commit', _('Submit')) }</p>
${ h.html.tags.end_form() }

<p><a href="${ h.url_for('package', packagename=c.package.name) }">${ _('Back to package details') }</a>
