# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Site contact') }</h1>

<p>You can get directly with the debexpo team. Asheesh Laroia and Andrey Rahmatullin are the main people involved. For now, the best way to reach them is by emailing the debexpo <a href="http://lists.alioth.debian.org/mailman/listinfo/debexpo-devel">development list</a> (<a href="http://lists.alioth.debian.org/pipermail/debexpo-devel/">Archives</a>). You can also find information about that on the <a href="http://wiki.debian.org/Debexpo">Debian wiki page</a>.</p>

<p>In case of technical problems please check the Q&amp;A section first. <strong>${ _('Site email') }</strong>: <a href="mailto: ${ c.config['debexpo.email'] }">${ c.config['debexpo.email'] }</a></p>

<h1>Development</h1>

<p>debexpo has had a long history. Andrey (wRAR) and Asheesh (paulproteus) are bringing it back, and we need help. We hope you'll hang out in #debexpo on irc.debian.org and chat with us.</p>

