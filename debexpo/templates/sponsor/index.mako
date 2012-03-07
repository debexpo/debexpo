# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>The sponsoring process</h1>

<p>As sponsored maintainer you do not have upload permissions to the Debian repository. Therefore you have three possibilities to get your package into Debian:</p>

<ul>
    <li>Join a packaging team</li>
    <li>Ask the <tt>debian-mentors</tt> mailing list</li>
    <li>Talk directly to people willing to sponsor your package</li>
</ul>

<p>A sponsor, regardless of how you found one will ${ h.tags.link_to("review", h.url('intro-reviewers')) } your package. Everyone is invited to review packages, including yourself. We encourage you to review other people's packages - both of you will benefit.</p>

<h2>Join a packaging team</h2>

<p>There are teams in Debian who maintain packages collaboratively. If your package deals with libraries for programming languages or is part of an ecosystem of associated packages, think of KDE or Gnome packages for example, you may want to join the respective team. Have a look at the <a href="http://wiki.debian.org/Teams/#Packaging_teams">(incomplete) list of packaging teams</a> in Debian.</p>

<p>Please note, each of those teams may have their own workflows and policies covering how to deal with package uploads. Contact their respective mailing lists and home pages to learn more.</p>

<h2>File a RFS bug against the <tt>sponsorship-requests</tt> pseudo-package</h2>

<p>If your package does not match the interests of any team or you are not sure whether a team could be interested in your package, please report a bug against <tt><a href="http://bugs.debian.org/cgi-bin/pkgreport.cgi?pkg=sponsorship-requests">sponsorship-requests</a></tt> pseudo-package to draw attention to your package. Your bug report should be formatted according to our RFS ("<em>request for sponsorship</em>") template. If you uploaded your package to ${ config['debexpo.sitename'] }, a RFS template can be shown on your package page.</p>

<p><em>If you are unsure or in doubt, choose this alternative</em>.</p>

<p>Typically you will reach the greatest audience by filing a bug. Eventually also some non-uploading reviewer may have a look at your package. Please do not worry if you get no answer: It happens from time to time that all interested people might be distracted or busy. It does not mean your package is bad. Feel free to poste a follow-up message after a few weeks or try any of the alternative methods to find a sponsor. </p>

<h2>Finding a sponsor</h2>

<p>If you want, you can contact sponsors willing to upload packages of other maintainers directly. <em>Please do not send out mass emails!</em> Instead watch out for their individual requirements and guidelines. Contact individuals only if your package is compatible to their respective requirements and matches their area of interest. To tell apart sponsors who are interested in your package from those who are not, we asked developers to formulate their own sponsor traits. Please read them carefully and compare your package with their expectations.</p>

<p>Similarly, you can also try to get in touch with other package maintainers directly. This makes sense if you prepared a package which extends the functionality of a related package in a useful way or can be used together. Consider you packaged log analysis tool for a web server, the maintainer of that web server might be interested to sponsor you. If you consider to contact a maintainer of such a related package directly, make sure he is actually able to sponsor you. Remember: Only Debian Developer are allowed to sponsor packages. You can identify developers by looking up their name at <a href="http://db.debian.org/">db.debian.org</a>.</p>

<h2>Sponsor guidelines</h2>

To help you find a sponsor interested in your package, they can formulate sponsor traits for either social or technical aspects. Additionally a sponsor may not usually be interested in every package but only in a certain category.

