# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

${ c.custom_html }

<h1>Introduction for maintainers</h1>

<h2>Welcome to ${ c.config['debexpo.sitetitle'] }</h2>

<p>We are glad that you found your way to our web site. Honestly the whole web site is just there to get your work into Debian. Your contribution is appreciated and it would be a pity if you did not find a sponsor to upload your packages. Read on to see in what ways we will be helping you find a sponsor.</p>


<h3>How will my package get into Debian?</h3>

<p>This web site is a public package repository of source packages. You can upload your package to this server (through special tools like 'dupload' or 'dput') and after a few checks it will be stored in our repository. ${ h.tags.link_to("Interested sponsors", h.url(controller='sponsor', action='index')) } can then download the package and upload it to Debian. So the basic procedure is:</p>

<ol>
    <li><strong>${ h.tags.link_to("Sign up for an account", h.url(controller='register', action='register')) }</strong>. Getting an account on this server is an automatic process and will just take a moment. We require registration so we have a valid email address where sponsors can reach you.</li>
    <li><strong>Upload your package</strong> to <tt>mentors.debian.net</tt>. You do not need to put your packages into any other web space on the Internet. Everybody will be able to download your package using either the web browser, the '<tt>dget</tt>' tools or even through a simple run of <tt>apt-get source ....</tt></li>
    <li>Have a look to your ${ h.tags.link_to("personal package page", h.url(controller='package', action='my')) }. Your uploaded package should <strong>show up there</strong>. From there you can toggle several settings and retrieve the RFS (request-for-sponsorship) template</li>
    <li>Your package is on display on the main page of ${ c.config['debexpo.sitetitle'] }, if you enable the "<i>Needs a Sponsor</i>" button, so interested sponsors will see it and hopefully check it out.</li>
    <li>You will be shown a <strong>RFS (request-for-sponsorship) template</strong> that you should send to the debian-mentors mailing list to draw attention to your package.</li>
    <li>Your package will hopefully be reviewed by a sponsor and either acknowledge your work and <strong>upload your package to Debian</strong>, or ask you to address some problems.</li>
</ol>

<h3>How to upload packages?</h3>

<p>You need to use <a href="http://packages.debian.org/dput"><tt>dput</tt></a> to upload packages.
% if c.logged_in:

See your ${ h.tags.link_to("account page", h.url('my')) } to see how to configure it, or put the following content to your <tt>~/.dput.cf</tt> file:</p>

<pre>
[debexpo]
fqdn = ${ config['debexpo.sitename'] }
incoming = /upload/${ c.user.email }/${ c.user.get_upload_key() }
method = http
allow_unsigned_uploads = 0
</pre>
% else:

You need to configure <tt>dput</tt>. Please ${ h.tags.link_to("login", h.url(controller='login', action='index')) } to see your personal <tt>~/.dput.cf</tt> here.

% endif

<p>Once you have it set up, you can run it from your shell like this:</p>

<pre>
$ dput debexpo your_sourcepackage_1.0.changes
</pre>

<h3>Will my name stay visible on the package?</h3>

<p>Yes. The Debian project appreciates the work you do. So you will be named as the official maintainer of the package in Debian. You will even get the bug reports if people discover problems in your package. Besides from not being able to upload the package directly into Debian you are treated as a full member of the community.</p>

<h3>What can I do if I don't find a sponsor?</h3>

<p>Don't become desperate. Sponsoring can take a while. Nonetheless, here are a few hints:</p>

<ul>
    <li>Ask again on the debian-mentors mailing list. Its common practice to ask again after a few weeks.</li>
    <li>Offer your package directly to developers. We made a ${ h.tags.link_to("a list of sponsors", h.url(controller='sponsor', action='index')) }, eventually willing to upload packages for you. <em>Please don't contact every sponsor listed there. Instead, read their individual requirements and choose the sponsor which matches you and your package best</em>.
</ul>
