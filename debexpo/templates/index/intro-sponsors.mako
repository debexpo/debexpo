# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

${ c.custom_html }

<h1>The sponsoring process</h1>

As sponsored maintainer you don't have upload permissions to the Debian repository. Therefore you have three possibilities to get your package into Debian:

<ul>
    <li>Join a packaging team</li>
    <li>Ask the <tt>debian-mentors</tt> mailing list</li>
    <li>Talk directly to people willing to sponsor your package</li>
</ul>

<h2>Join a packaging team</h2>

<p>There are teams in Debian who maintain packages collaboratively. If your package deals with libraries for programming langauges, or is about an ecosystem of associated packages, think of KDE or Gnome packages for example, you may want to join that team. Have a look to <a href="http://wiki.debian.org/Teams/#Packaging_teams">list of packaging teams</a> in Debian.</p>

<p>Please note, each of those teams may have their own workflows and policies. Contact their respective mailing lists to learn more.</p>

<h2>Ask the <tt>debian-mentors</tt> mailing list</h2>

<p>If your package does not match the interests of any team, or you are not sure whether a team could be interested in your package, please write to the <tt><a href="http://lists.debian.org/debian-mentors/">debian-mentors</a></tt> mailing list to draw attention to your package. Your request should be formatted according to our RFS ("<em>request for sponsorship</em>") template. If you uploaded your package to ${ config['debexpo.sitename'] }, a RFS template can be shown on your package page.</p>

<p>Don't worry if you get no answer: It does not mean your package is bad. Ask again after a few weeks if you did not find a sponsor by other means yet. </p>

<h2>Finding a sponsor</h2>

<p>If you want, you can write sponsors willing to upload packages to other maintainers directly. <strong>Don't contact them blindly!</strong> Instead watch out for their requirements and guidelines. Contact them only if your package is compatible to their individual requirements and matches their area of interest. To tell apart sponsors who are interested in your package and who are not, they can formulate their own sponsor metrics.</p>

<h2>Sponsor metrics</h2>

To help you finding a sponsor interested in your package, they can formulate sponsor metrics:

<h3>Packages interested in</h3>

<p>Sponsors typically are not interested to upload any package for you. They could, however, be interested if your package matches their area of interest. Please compare those package types with your package. Such categories eventually are certain programming languages your program is written in, a field of endeavour, or software fulfilling a certain task. </p>


<table>
    <tr>
        <th width="50%">Technical requirements</th>
        <th width="50%">Social requirements</th>
    <tr>
    <tr>
        <td>
            Debian allows several workflows and best practices to co-exist with each other. All packages <strong>must comply the <a href="http://www.debian.org/doc/debian-policy/">Debian policy</a></strong> as bare essential minimum, but some workflows and best practices beyond that are optional, but nonetheless mandatory <em>for you</em> asking that person to sponsor your upload.
        </td>
        <td>
            Some sponsors prefer to upload only packages from people, that fulfill certain social criterias. Please don't ask an uploader to sponsor your request if you don't match them.
        </td>
    </tr>
    <tr>
        <td>
    <dl>
            <dt>CDBS</dt>
            <dd>Your package makes use of the <a href="http://build-common.alioth.debian.org/">The Common Debian Build System</a></dd>

            <dt>Debhelper</dt>
            <dd>Your package makes use of the <a href="http://kitenet.net/~joey/code/debhelper/">debhelper</a> build system</dd>

            <dt>Custom debian/rules</dt>
            <dd>Your package is using a completely customized, yet <a href="http://www.debian.org/doc/debian-policy/ch-source.html#s-debianrules">policy compliant</a> <tt>debian/rules</tt> file</dd>

            <dt>NMUs</dt>
            <dd>Your package is a <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu">NMU</a></dd>

            <dt>QA uploads</dt>
            <dd>Your package is a <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu-qa-upload">QA upload</a></dd>

            <dt>Backports</dt>
            <dd>Your package is a <a href="http://backports-master.debian.org/">backported package</a></dd>

            <dt>Modified Tarballs</dt>
            <dd>Your package modified the original source tarball somehow in a way, it does not match the original checksum anymore</dd>

            <dt>VCS snapshot tarballs</dt>
            <dd>Your package is not based on a original source tarball at all, but is based on a VCS snapshot</dd>

            <dt>contrib/non-free packages</dt>
            <dd>Your package it targetting the <tt>contrib</tt> or <tt>non-free</tt> branches (<a href="http://www.debian.org/doc/debian-policy/ch-archive.html#s-sections">Information</a>)</dd>

            <dt>1.0 format packages</dt>
            <dd>Your package is using the 1.0 format (the traditional source format that is).</dd>

            <dt>3.0 format packages</dt>
            <dd>Your package is using the <a href="http://wiki.debian.org/Projects/DebSrc3.0">3.0/quilt</a> format.</dd>

            <dt>No embedded code copies</dt>
            <dd>Your package does <em>not</em> <a href="http://www.debian.org/doc/debian-policy/ch-source.html#s-embeddedfiles">make use of embedded code copies</a>.</dd>

            <dt>DEP-5 copyright</dt>
            <dd>Your package does make use of <a href="http://dep.debian.net/deps/dep5/">DEP-5</a> copyright files.</dd>

            <dt>Non-DEP5 copyright</dt>
            <dd>Your package does <em>not</em> make use of <a href="http://dep.debian.net/deps/dep5/">DEP-5</a> copyright files.</dd>

            <dt>Lintian cleanness</dt>
            <dd>Your package is <a href="http://lintian.debian.org/">Lintian clean</a> down to the informational level.</dd>
        </dl>
        </td>
        <td>

        <dl>
            <dt>Prospective DM/DD</dt>
            <dd>You are willing to become a <a href="http://wiki.debian.org/DebianMaintainer">Debian Maintainer</a>/<a href="http://wiki.debian.org/DebianDeveloper">Debian Developer</a> some day.</dd>

            <dt>(Willing to be) DM</dt>
            <dd>You are a <a href="http://wiki.debian.org/DebianMaintainer">Debian Maintainer</a> already, or you plan to become one soon.</dd>

            <dt>(Willing to enter) NM</dt>
            <dd>You are in the <a href="https://nm.debian.org/">New Maintainer</a> process to become a developer already, or you plan to apply soon.</dd>

            <dt>Signed GPG key</dt>
            <dd>Your GPG matches the <a href="http://lists.debian.org/debian-devel-announce/2010/09/msg00003.html">guidelines of the Debian keyring maintainers</a> and/or is signed by any Debian developer.</dd>

            <dt>No one time uploads</dt>
            <dd>You want to maintain the package you want to have sponsored in the forseeable future. Your package is not a single shot.</dd>

            <dt>Sharing a time zone<dt>
            <dd>You share a time zone with your sponsors. This can be useful to get together more easily.</dd>

            <dt>Possibility to meet-up</dt>
            <dd>You are living close to your sponsor and you are willing to meet him eventually</dd>

            <dt>Having already packages in Debian</dt>
            <dd>You are already maintaining packages in Debian</dd>
        </dl>
        </td>
    </tr>
</table>



<h3>Social requirements</h3>

<table width="100%">
    <tr>
        <th width="30%">Sponsor name and contact data</th>
        <th width="35%">Sponsor guidelines</th>
        <th width="35%">Social Requirements</th>
    </tr>
<%
    def preferred(flag):
        if flag:
            return "(preferred)"
        else:
            return ""
%>
% for sponsor in c.sponsors:
    <tr>
        <td>
            <span style="font-size:120%"><strong>${ sponsor.user.name }</strong></span>
            <br />
            <ul>
            % if sponsor.user.email and sponsor.allowed(c.constants.SPONSOR_CONTACT_METHOD_EMAIL):
                <li>Email: ${ sponsor.user.email } ${ preferred(sponsor.contact == c.constants.SPONSOR_CONTACT_METHOD_EMAIL) }</li>
            % endif
            % if sponsor.user.ircnick and sponsor.allowed(c.constants.SPONSOR_CONTACT_METHOD_IRC):
                <li>IRC: ${ sponsor.user.ircnick } ${ preferred(sponsor.contact == c.constants.SPONSOR_CONTACT_METHOD_IRC) }</li>
            % endif
            % if sponsor.user.jabber and sponsor.allowed(c.constants.SPONSOR_CONTACT_METHOD_JABBER):
                <li>Jabber: ${ sponsor.user.jabber } ${ preferred(sponsor.contact == c.constants.SPONSOR_CONTACT_METHOD_JABBER) }</li>
            % endif
            </ul>
            <strong>Packages interested in</strong>
            <p>${ sponsor.get_types() | n}</p>
        </td>
        <td>
            <ul>
            <% requirements = sponsor.database_to_technical_requirements() %>
            % for requirement in c.constants.SPONSOR_TECHNICAL_REQUIREMENTS:
                % if requirement[1] in requirements:
                    <li>${ requirement[0] }</li>
                % endif
            % endfor
            </ul>
            <p>${ sponsor.get_guidelines() | n}</p>
        </td>
        <td>
            <ul>
            <% social_requirements = sponsor.database_to_social_requirements() %>
            % for requirement in c.constants.SPONSOR_SOCIAL_REQUIREMENTS:
                % if requirement[1] in social_requirements:
                    <li>${ requirement[0] }</li>
                % endif
            % endfor
            </ul>
            ${ sponsor.get_social_requirements() | n}
        </td>
    </tr>
% endfor
</table>
