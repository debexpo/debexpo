# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>Questions &amp; Answers</h1>

${ c.config['debexpo.sitename'] } is a rather complex service. Things can go wrong on your side or on this server. Before contacting the support please see if your question is answered here: 

<h2>Getting started</h2>
<h3>How do I build a package?</h3>

	<p>If you want to learn how to create a proper Debian package you can find some interesting documentation to start with at:</p>

	<ul>
		<li><a href="http://www.debian.org/doc/manuals/maint-guide/">New Maintainer's Guide</a></li>
		<li><a href="http://wiki.debian.org/HowToPackageForDebian">HowToPackageForDebian</a> (Debian Wiki)</li>
		<li><a href="http://www.debian.org/doc/manuals/developers-reference/index.html">Developer's Reference</a></li>
	</ul>

<h3>What is the Debian policy?</h3>

<p>Every package must comply with the <a href="http://www.debian.org/doc/debian-policy/ch-scope.html">Debian policy</a> before it can enter the Debian distribution. This is a document which describes the structure and contents of the Debian archive and several design issues of the operating system, as well as technical requirements that each package must satisfy to be included in the distribution.</p>

<h3>What is Lintian?</h3>

<p>Lintian is a Debian package checker (and available as <a href="http://packages.debian.org/lintian">Debian package</a> so you can run it yourself). It can be used to check binary and source packages for compliance with the Debian policy and for other common packaging errors.</p>

<p>Packaging for Debian is rather complex because one has to consider hundreds of guidelines to make the package "policy compliant". Lintian tries to address this issue by providing an automated static analysis framework. You can learn more about Lintian in the <a href="http://lintian.debian.org/manual/index.html">Lintian User's Manual</a>. </p>

<h2>Your Account</h2>

<h3>Why do I not receive a confirmation email?</h3>

<p>First make sure that you signed the package with the proper PGP key. Next check where you uploaded your package. By default the dput and dupload tools upload to Debian's official FTP master server. That server will silently drop your upload. If the problem persist please send an email to <strong>${ _('Site email') }</strong>: <a href="mailto: ${ c.config['debexpo.email'] }">${ c.config['debexpo.email'] }</a> if you require assistance. </p>

<h3>My binary packages do not show up</h3>

<p>The current policy on ${ c.config['debexpo.sitename'] } is to deliberately throw away the binary packages. This is done for two main reasons. First, it saves a lot of disk space. And second, in the past Debian users downloaded the packages and used them carelessly to get brand-new versions. This led to a lot of support questions. So we decided to just keep the source packages.</p>
