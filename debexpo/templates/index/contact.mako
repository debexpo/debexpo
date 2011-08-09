# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Site contact') }</h1>

<p>You can get directly with the debexpo team. In case of technical problems please check the ${ h.tags.link_to( _('Q & A'), h.url('qa')) } section and the <a href="http://wiki.debian.org/Debexpo">Debian wiki</a> first. Please do not use this contact address for sponsor requests or packaging questsion, write to the <a href="http://lists.debian.org/debian-mentors/">debian-mentors mailing list</a> instead.</p>

<p><strong>${ _('Site email') }</strong>: <a href="mailto: ${ c.config['debexpo.email'] }">${ c.config['debexpo.email'] }</a>.</p>

<h1>Development</h1>

<p>${ c.config['debexpo.sitename'] } started 2008 as "Google Summer of Code" project by Jonathan Lamb, mentored and further developed by Christoph Haas (<em>Signum</em>). <strong>HERE IS MORE TO BE ADDED. WHO KNOWS WHO CONTRIBUTED SIGNIFICANTLY SINCE THEN?</strong>. Andrey Rahmatullin (<em>wRAR</em>) and Asheesh Laroia (<em>paulproteus</em>) are bringing it back, and we need help. We hope you'll hang out in <tt>#debexpo</tt> on <a href="irc://irc.debian.org/debexpo">irc.debian.org</a> and chat with us.</p>

<p>For now, the best way to reach developers is by emailing the debexpo <a href="http://lists.alioth.debian.org/mailman/listinfo/debexpo-devel">development list</a> (<a href="http://lists.alioth.debian.org/pipermail/debexpo-devel/">Archives</a>).</p>
