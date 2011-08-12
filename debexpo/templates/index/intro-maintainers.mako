# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

${ c.custom_html }

<h1>Introduction for maintainers</h1>

<h2>Welcome to ${ c.config['debexpo.sitetitle'] }</h2>

<p>We are glad that you found your way to our web site. Honestly the whole web site is just there to get your work into Debian. Your contribution is appreciated and it would be a pity if you did not find a sponsor to upload your packages. Read on to see in what ways we will be helping you find a sponsor.</p>


<h3>How will my package get into Debian?</h3>

<p>This web site is a public package repository of source packages. You can upload your package to this server (through special tools like 'dupload' or 'dput') and after a few checks it will be stored in our repository. Interested sponsors can then download the package and upload it to Debian. So the basic procedure is:</p>

<ul>
    <li>${ h.tags.link_to("Sign up for an account", h.url(controller='register', action='register')) }. Getting an account on this server is an automatic process and will just take a moment. We require registration so we have a valid email address where sponsors can reach you.</li>
    <li>Upload your package to mentors.debian.net. You don not need to put your packages into any other web space on the Internet. Everybody will be able to download your package using either the web browser, the 'dget' tools or even through a simple run of apt-get source ....</li>
    <li>Your package is on display on the main page of ${ c.config['debexpo.sitetitle'] } so interested sponsors will see it and hopefully check it out.</li>
    <li>You will be shown a RFS (request-for-sponsorship) template that you can send to the debian-mentors mailing list to draw attention to your package.</li>
    <li>Finally a sponsor will hopefully pick up your package and upload it on your behalf. Bingo - your package is publicly available in Debian. And this server will automatically send you an email in case you did not notice the upload.</li>
</ul>

<h3>Is my package technically okay?</h3>

<p>When you upload your package to ${ c.config['debexpo.sitename'] } it will automatically be checked for common mistakes. You will get an information email after the upload. Either your package contains bugs and will be rejected, or the package is clean except for some minor technical issues. You will get hints about how to fix the package. If the email tells you that your package is fine then a sponsor will still do further checks. Don't worry too much. If your package is accepted by mentors.debian.net then let the sponsor help you with the rest.

<h3>How to upload packages?</h3>

<p>You need to use <a href="http://packages.debian.org/dput">dput</a> to upload packages.
See your ${ h.tags.link_to("account page", h.url('my')) } to see how to configure it.</p>
<p>Once you have it set up, you can run it from your shell like this:</p>
<pre>
dput debexpo yourpackage_yourversion_arch.changes
</pre>


<h3>How long will it take until my upload is available to sponsors?</h3>

<p>Our automatic processes will check for newly incoming packages every 30 seconds. We will process your package and check some things statically. You will usually get a reply by email within a few minutes.</p>

<h3>Will my name stay visible on the package?</h3>

<p>Yes. The Debian project appreciates the work you do. So you will be named as the official maintainer of the package in Debian. You will even get the bug reports if people discover problems in your package. Besides from not being able to upload the package directly into Debian you are treated as a full member of the community.</p>
