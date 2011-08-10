# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>
${ c.custom_html }

<h1>Welcome to ${ c.config['debexpo.sitename'] }</h1>

<!--
<div class="warning">
	<p>
	This page is currently on a public beta test! All uploads and account data will be wiped upon migration to this new service. Use the old <a href="http://mentors.debian.net">mentor service</a> for your data.
	</p>
</div>
-->

<p>Only approved members of the Debian project - so-called <i>Debian developers</i> - are granted the permission to upload software packages into the Debian distribution. Still a large number of packages is maintained by non-official developers. How do they get their work into Debian when they are not allowed to upload their own packages directly? By means of a process called <i>sponsorship</i>. Don't worry - it does not deal with money. Sponsorship means that a Debian developer uploads the package on behalf of the actual maintainer. The Debian developer will also check the package for technical correctness and help the maintainer to improve the package if necessary. Therefore the sponsor is sometimes also called a mentor.</p>

<p>You can even help us to review packages if you are not a developer. We appreciate your efforts as well.</p>

<ul>
	<li>I want to have my package uploaded to Debian: Please go to ${ h.tags.link_to("our introductory page", h.url('intro-maintainers')) } for maintainers and learn how to use ${ c.config['debexpo.sitename'] }.</li>
	<li>I am a Debian developer and want to offer sponsorship: Please go to ${ h.tags.link_to("our introductory page for sponsors", h.url('intro-sponsors')) } to learn how you can help best.</li>
	<li>I am a Debian maintainer or a skilled sponsored maintainer and want to help: Please go to ${ h.tags.link_to("our page dedicated to reviewers", h.url('intro-reviewers')) }.</li>
</ul>

<p>You can <a href="http://wiki.debian.org/Debexpo">read more about debexpo on the Debian Wiki</a>.</p>

   
<h1>Recently uploaded packages</h1>

<%include file="../packages/list.mako" />
