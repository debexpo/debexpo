# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>Introduction for maintainers: How will my package get into Debian</h1>

<p>We are glad that you found your way to our web site. Honestly the whole web site is just there to get your work into Debian. Your contribution is appreciated and it would be a pity if you did not find a sponsor to upload your packages. Read on to see in what ways we will be helping you find a sponsor.</p>

<h2>1. Find a requested package</h2>

<p>Debian is a distribution, not a general purpose repository. Many of us do not believe <em>every</em> piece of free software necessarily belongs in Debian. Please do not treat Debian as a platform to advertise your own software, unless there is some <em>real</em> request for it. That said, there is no one who ultimately judges about that. Eventually you may get some feedback on that discussion after filing your WNPP bug (see below) however you are free to interpret that as a suggestion, not as a final vote. After all, you need to find a sponsor believing in the benefit of having your package in Debian. Please have a look at our ${ h.tags.link_to("sponsors page", h.url(controller='sponsor', action='index')) } to learn about personal interests of sponsors.</p>

<p>If you want to contribute to Debian, but you do not know which packages to contribute to, take a look at "Request for help" (<em>RFH</em>), "Request for adopter" (<em>RFA</em>), "Orphaned package" (<em>O</em>) and "Request for package" (<em>RFP</em>) bugs. See <em>WNPP</em> below.</p>

<h2>2. File a WNPP bug</h2>

<p><a href="https://www.debian.org/devel/wnpp/">Work-Needing and Prospective Packages</a> (<em>WNPP</em>) is our system of announcing your intent to markup packages being worked on. In particular it is a bug against the <a href="https://bugs.debian.org/cgi-bin/pkgreport.cgi?pkg=wnpp">WNPP pseudo package</a> (<a href="http://wnpp.debian.net/">or use a nice frontend</a> to browse <em>WNPP</em> bugs). If you want to package something not currently available in Debian, the very first step should be to file an "Intent to package" (<em>ITP</em>) bug against <em>WNPP</em>. You may want to use the <tt><a href="https://packages.debian.org/squeeze/reportbug">reportbug</a></tt> tool to achieve that by selecting "<em>wnpp</em>" as package to report a bug to.</p>

<h2>3. Make the package</h2>

<p>Debian packages must comply to several normative requirements and guidelines. We can't give you exhaustive instructions on how to build packages here. In short, we expect you to provide a <em>source package</em> complying to the Debian policy at least (see below). Please take a look at those excellent resources:</p>

    <dl>
        <dt><a href="https://www.debian.org/doc/debian-policy/">The Debian Policy Manual</a></dt>
        <dd>A must-read resource to learn about technical specification and technical requirements of Debian packages.</dd>
        <dt><a href="https://www.debian.org/doc/manuals/maint-guide/">New Maintainer's Guide</a></dt>
        <dd>A must-read resource to learn basics of Debian source packages</dd>
        <dt><a href="https://www.debian.org/doc/manuals/packaging-tutorial/packaging-tutorial">Lucas Nussbaum's packaging tutorial</a></dt>
        <dd>A quick introduction to Debian packaging</dd>
        <dt><a href="https://www.debian.org/doc/manuals/developers-reference/">Developer's Reference</a></dt>
        <dd>A comprehensive manual describing typical workflows and best practices related to Debian packages</dd>
        <dt><a href="https://wiki.debian.org/DebianMentorsFaq">Debian Mentors FAQ</a> (Debian Wiki)</dt>
        <dd>Another valuable resource to learn about common terms and workflows related to Debian</dd>
    </dl>


<h2>4. Publish your package</h2>

<p>This web site is a public package repository of source packages. You can upload your package to this server (through special tools like '<tt><a href="https://packages.debian.org/squeeze/dupload">dupload</a></tt>' or '<tt><a href="https://packages.debian.org/squeeze/dput">dput</a></tt>') and after a few checks it will be stored in our repository. ${ h.tags.link_to("Interested sponsors", h.url(controller='sponsor', action='index')) } can then download the package and upload it to Debian.</p>

<h3>Using ${ c.config['debexpo.sitetitle'] }</h3>

<ul>
    <li><strong>${ h.tags.link_to("Sign up for an account", h.url(controller='register', action='register')) }</strong>. Getting an account on this server is an automatic process and will just take a moment. We require registration so we have a valid email address where sponsors can reach you.</li>
    <li><strong>Upload your package</strong> to <tt>${ config['debexpo.sitename'] }</tt>. You do not need to put your packages into any other web space on the Internet. Everybody will be able to download your package using either the web browser, the '<tt>dget</tt>' tools or even through a simple run of <tt>apt-get source ....</tt></li>
    <li>Have a look at your ${ h.tags.link_to("personal package page", h.url(controller='packages', action='my')) }. Your uploaded package should <strong>show up there</strong>. From there you can toggle several settings and retrieve the RFS (request-for-sponsorship) template</li>
    <li>Your package is on display on the main page of ${ c.config['debexpo.sitetitle'] } (if you enable the "<i>Needs a Sponsor</i>" button) so interested sponsors will see it and hopefully check it out.</li>
    <li>You will be shown a <strong>RFS (request-for-sponsorship) template</strong> that you should send out as a bug report filed against the <em>sponsorship-requests</em> pseudo-package to draw attention to your package.</li>
</ul>

<h3>How to upload packages to <tt>${ config['debexpo.sitename'] }?</tt></h3>

<p>You need to use <a href="https://packages.debian.org/dput"><tt>dput</tt></a> to upload packages. We accept your uploads through <em>HTTP</em> or <em>FTP</em>. All packages <strong>must be signed</strong> with the GnuPG key you configured in your control panel. </p>

<table>
    <tr>
        <td width="50%">HTTP uploads</td>
        <td width="50%">FTP uploads</td>
    </tr>
    <tr>
        <td>
            <p>To use HTTP put the following content to your <tt>~/.dput.cf</tt> file:</p>

<pre>
[mentors]
fqdn = ${ config['debexpo.sitename'] }
incoming = /upload
method = http
allow_unsigned_uploads = 0
progress_indicator = 2
# Allow uploads for UNRELEASED packages
allowed_distributions = .*
</pre>

        </td>
        <td>
            <p>You can use <em>FTP</em> to upload packages to ${ c.config['debexpo.sitetitle'] }. If you prefer that method make sure you sign your uploads with your GPG key! This is the corresponding <tt>~/.dput.cf</tt> file:</p>

<pre>
[mentors-ftp]
fqdn = ${ config['debexpo.sitename'] }
login = anonymous
progress_indicator = 2
passive_ftp = 1
incoming = /
method = ftp
allow_unsigned_uploads = 0
# Allow uploads for UNRELEASED packages
allowed_distributions = .*
</pre>
        </td>
    </tr>
</table>

<p>Once you have it set up, you can run it from your shell like this:</p>

<pre>
$ dput mentors your_sourcepackage_1.0.changes
</pre>

If you did everything right, you will get a confirmation mail from our site and you can start seeking a sponsor for your package.

<h2>5. Find a sponsor</h2>

<p>Once your package is publicly available on any resource, including but not limited to ${ c.config['debexpo.sitetitle'] } you may start searching for a sponsor for your package. If you have already uploaded packages to Debian, you should ask your former sponsor. A sponsor is any <a href="https://wiki.debian.org/DebianDeveloper">Debian Developer</a> willing to upload your package to Debian on your behalf. Have a look to our ${ h.tags.link_to("sponsor's page", h.url(controller='sponsor', action='index')) } to learn more on sponsors and how to find one.</p>

<p>The main point of the sponsoring process is to review your package to make sure it meets our technical requirements. Everyone can and should review other people's packages. Also, a clean package will increase your likelihood to find a sponsor. Please take a look at our page ${ h.tags.link_to("about package reviews", h.url('intro-reviewers')) }.</p>

<h3>The relation between you and your sponsor</h3>

<p>A sponsor is not technically responsible for your package. <strong>You</strong> will be listed as the official maintainer of the package in Debian. You will even get the bug reports if people discover problems in your package. Apart from not being able to upload the package directly into Debian you are treated as a full member of the community. The Debian project appreciates the work you do.</p>

<h3>What can I do if I don't find a sponsor?</h3>

<p>Do not give up. Sponsoring can take a while. Nonetheless, here are a few hints:</p>

<ul>
    <li>File a follow-up request to your existing <em>sponsorship-requests</em> pseudo-package.</li>
    <li>Offer your package directly to relevant teams and individual developers. We made a ${ h.tags.link_to("a list of sponsors", h.url(controller='sponsor', action='index')) }, eventually willing to upload packages for you. <em>Please don't contact every sponsor listed there. Instead, read their individual requirements and choose the sponsor which matches you and your package best</em>.</li>
</ul>

<h2>6. Getting an upload to Debian</h2>

<p>Once you find a sponsor interested in your package, he will <em>sponsor</em> it. That means reviewing, building and testing it and then uploading it and then uploading it to Debian. You will get notified by <em>dak</em> - the software used by Debian to manage its repositories - about the upload. Please note, if your package was not at all in Debian before, it needs manual approval by <a href="https://ftp-master.debian.org/">ftpmasters</a> to clear the <a href="https://ftp-master.debian.org/new.html">NEW queue</a>. They will do consistency checks, and review your <tt>debian/copyright</tt> file whether your package matches the <a href="https://www.debian.org/social_contract#guidelines">Debian Free Software Guidelines</a>. ftpmaster's opinion is binding here for both your sponsor and you.</p>

<h2>7. Maintaining your package in Debian</h2>

<p>Please see the corresponding chapter in the <a href="https://www.debian.org/doc/manuals/maint-guide/update">New Maintainer's Guide</a> to get the idea. Whenever you feel like, you should update your package in Debian. The general procedure is not different from your fist upload. Please upload your updated package to ${ config['debexpo.sitename'] } and notify your former sponsor about your change. Alternatively, follow ${ h.tags.link_to("the usual procedures", h.url(controller='sponsor', action='index')) }.</p>

<p>If your package passes through the sponsoring process for <em>a few</em> successive uploads without any notable correction by your sponsor, you can become a <a href="https://wiki.debian.org/DebianMaintainer">Debian Maintainer</a> which grants you limited upload rights to Debian directly. Get in touch with your sponsor to discuss your chances here. You can also <a href="https://www.debian.org/devel/join/">become a Debian Developer</a> giving you full membership in the project.</p>

