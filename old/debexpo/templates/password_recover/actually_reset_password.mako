# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Okay! You have a new password')}</h1>

<p>You can use this new password to log in. Copy it carefully to your clipboard,
and then paste it into a login box.</p>

<p>Don't forget to change it!</p>

<div style="margin-left: 5em; border: dotted 1px; padding: 2px;">${ c.new_password }</div>
