# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Site contact') }</h1>

<p>You can get in direct contact with the debexpo team. In case of technical problems please check the ${ h.tags.link_to( _('Q & A'), h.url('qa')) } section and the <a href="http://wiki.debian.org/Debexpo">Debian wiki</a> first. <strong>Please do not use this contact address for sponsor requests or packaging questions</strong>, write to the <a href="http://lists.debian.org/debian-mentors/">debian-mentors mailing list</a> instead or ${ h.tags.link_to( _('file a RFS bug'), h.url(controller="sponsor", action="rfs-howto") ) } respectively.</p>

<p><strong>${ _('Site email') }</strong>: <a href="mailto: ${ c.config['debexpo.email'] }">${ c.config['debexpo.email'] }</a>.</p>

<p>Currently Asheesh Laroia (<em>paulproteus</em>), Paul Wise (<em>pabs</em>) and Arno Töll (<em>daemonkeeper</em>) are maintaining this service.</p>

<h1>Development</h1>

<p>We are looking for new contributors. If you want to contribute or improve ${ c.config['debexpo.sitename'] }, come to <tt>#debexpo</tt> on <a href="irc://irc.debian.org/debexpo">irc.debian.org</a> and chat with us.</p>

