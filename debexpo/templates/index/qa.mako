# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>Questions &amp; Answers</h1>

${ c.config['debexpo.sitename'] } is a rather complex service. Things can go wrong on your side or on this server. Before contacting the support please see if your question is answered here: 

<h2>Getting started</h2>
<h3>How do I build a package?</h3>

    <p>If you want to learn how to create a proper Debian package you can find some interesting documentation to start with:</p>

    <dl>
        <dt><a href="https://www.debian.org/doc/debian-policy/">The Debian Policy Manual</a></dt>
        <dd>A must read resource to learn about technical specification and technical requirements of Debian packages.</dd>
        <dt><a href="https://www.debian.org/doc/manuals/maint-guide/">New Maintainer's Guide</a></dt>
        <dd>A must read resource to learn basics of Debian source packages</dd>
        <dt><a href="https://www.debian.org/doc/manuals/packaging-tutorial/packaging-tutorial">Lucas Nussbaum's packaging tutorial</a></dt>
        <dd>A quick introduction to Debian packaging</dd>
        <dt><a href="https://www.debian.org/doc/manuals/developers-reference/">Developer's Reference</a></dt>
        <dd>A comprehensive manual describing typical workflows and best practices related to Debian packages</dd>
        <dt><a href="https://wiki.debian.org/DebianMentorsFaq">Debian Mentors FAQ</a> (Debian Wiki)</dt>
        <dd>Another valuable resource to learn about common terms and workflows related to Debian</dd>
    </dl>

<h3>What is the Debian policy?</h3>

<p>Every package must comply with the <a href="https://www.debian.org/doc/debian-policy/ch-scope.html">Debian policy</a> before it can enter the Debian distribution. This is a document which describes the structure and contents of the Debian archive and several design issues of the operating system, as well as technical requirements that each package must satisfy to be included in the distribution.</p>

<p>The policy is not a tutorial. Its a technical manual which specifies normative requirements of packages. Read it to learn package specifications. If you don't know how to package something for Debian, please read additionally the <a href="https://www.debian.org/doc/manuals/maint-guide/">New Maintainer's Guide</a>.</p>

<h3>Is my package technically okay?</h3>

<p>When you upload your package to ${ c.config['debexpo.sitename'] } it will automatically be checked for common mistakes. You will get an information email after the upload. Either your package contains bugs and will be rejected, or the package is clean except for some minor technical issues. You will get hints about how to fix the package. If the email tells you that your package is fine then a sponsor will still do further checks. Don't worry too much. If your package is accepted by mentors.debian.net then let the sponsor help you with the rest.

<h3>What is Lintian?</h3>

<p>Lintian is a Debian package checker (and available as <a href="https://packages.debian.org/lintian">Debian package</a> so you can run it yourself). It can be used to check binary and source packages for compliance with the Debian policy and for other common packaging errors.</p>

<p>Packaging for Debian is rather complex because one has to consider hundreds of guidelines to make the package "policy compliant". Lintian tries to address this issue by providing an automated static analysis framework. You can learn more about Lintian in the <a href="https://lintian.debian.org/manual/index.html">Lintian User's Manual</a>. </p>

<h2>Your Account</h2>

<h3>Why do I not receive a confirmation email?</h3>

<p>First make sure that you signed the package with the proper PGP key. Next check where you uploaded your package. By default the dput and dupload tools upload to Debian's official FTP master server. That server will silently drop your upload. If the problem persist please send an email to <strong>${ _('Site email') }</strong>: <a href="mailto: ${ c.config['debexpo.email'] }">${ c.config['debexpo.email'] }</a> if you require assistance. </p>

<h3>My binary packages do not show up</h3>

<p>The current policy on ${ c.config['debexpo.sitename'] } is to deliberately throw away the binary packages. This is done for two main reasons. First, it saves a lot of disk space. And second, in the past Debian users downloaded the packages and used them carelessly to get brand-new versions. This led to a lot of support questions. So we decided to just keep the source packages.</p>

<h3>How long will it take until my upload is available to sponsors?</h3>

<p>If you upload via HTTP, which is what we recommend, then it will take between 0 and 2 minutes.</p>

<p>If you upload via FTP, which you must do if a package is too large for the HTTP uploader, then there can be up to a 30 minute delay before your package gets processed.</p>

<p>During those 0-2 minutes, the server does quality assurance and other checks on your package. You will receive an email when it is ready.</p>

<h2>Information for sponsors</h2>

<h3>What is a sponsor?</h3>

<p>Someone who uploads the package and is responsible for the package in the archive. The sponsor is responsible for the quality of the package and checks the work of the package maintainer to improve his skills.</p>

<h3>Why should I sponsor uploads</h3>

<p>Thanks for your interest. There are a lot of sponsorees waiting for a Developer to help them with their packages, and if you want to help with the New Maintainer process this is a good step to get involved.</p>

<h3>What to do for sponsoring?</h3>

<p>Look for packages that you would like to sponsor on this website. Once you have found some you should download, build and test them. Please notify your sponsoree of every problem that you find in order to give him a chance to fix them. We believe that it is of uttermost importance to stay in contact with your sponsorees to keep them interested in working on Debian. Moreover, they will also learn how to maintain packages within a team and will learn skills that are crucial for Debian Developers more easily. </p>

