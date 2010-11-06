# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

% if c.user is not None:

<h1>${ _('''%s's personal package archive''') % c.user.name }</h1>

<p>${ _('''To access these personal package archives, insert the following lines into your <tt>/etc/apt/sources.list</tt>:''') | n }</p>

<pre>
deb ${ c.config['debexpo.server'] }/ppa/${ c.user.email } distribution component1 [component2 ...]
deb-src ${ c.config['debexpo.server'] }/ppa/${ c.user.email } distribution component1 [component2 ...]
</pre>

<p>${ _('Note: Make sure you replace the <i>distribution</i> and <i>component</i> variables in the above lines.') | n }</p>

% else:

<h1>${ _('Personal package archives') }</h1>

<p>${ _('The user you have requested PPA details on cannot be found.') }</p>

% endif
