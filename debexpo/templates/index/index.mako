# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>Welcome to ${ c.config['debexpo.sitename'] }</h1>

<p>Only approved members of the Debian project (Debian Developers) are granted the permission to upload software packages into the Debian distribution. Still a large number of packages is maintained by non-official developers. How do they get their work into Debian when they are not allowed to upload their own packages directly? By means of a process called <em>sponsorship</em>. Sponsorship means that a Debian Developer uploads the package on behalf of the actual maintainer. The Debian Developer will also check the package for technical correctness and help the maintainer to improve the package if necessary. Therefore the sponsor is sometimes also called a mentor.</p>

<p>Note, not only Debian Developer are allowed to review packages. Everyone is encouraged to review packages! We appreciate your efforts as well.</p>

<h2>Getting your package into Debian</h2>

<p>See ${ h.tags.link_to("our introductory page for maintainers", h.url('intro-maintainers')) } and learn how to use ${ c.config['debexpo.sitename'] } and get your packages into Debian. Furthermore see ${ h.tags.link_to("our introductory page on sponsorship", h.url('sponsors')) } to learn how to get in touch with a sponsor.</p>

<p>If you are curious about <em>Debexpo</em>, the software which is running this site, you can <a href="http://wiki.debian.org/Debexpo">read more about Debexpo on the Debian Wiki</a>.</p>

<h1>Recently uploaded packages</h1>

<%include file="../packages/list.mako" />
