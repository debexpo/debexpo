# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

${ c.custom_html }

<h1>The sponsoring process</h1>

<h2>People willing to sponsor packages</h2>

<p>Below is an incomplete list of sponsors, willing to upload your package. Send your filled out RFS (request-for-sponsorship) template to the debian-mentors mailing list to draw attention to your package. If you don't get any feedback, or you think your package would perfectly fit to the requirements of one or more of the sponsors below, contact them directly:</li>

<p>Please don't be offensed if a sponsor you wrote won't reply you in time. He might be busy or short of time, as you write your mail</p>

<h2>Sponsor metrics</h2>
<h3>Packages interested in</h3>

<p>Sponsors typically are not interested to upload any package for you. They could, however, be interested if your package matches their area of interest. Please compare those package types with your package. Such categories eventually are certain programming languages your program is written in, a field of endeavour, or software fulfilling a certain task. </p>

<h3>Sponsor guidelines</h3>

<p>Debian allows several workflows and best practices to co-exist with each other. All packages must comply the <a href="http://www.debian.org/doc/debian-policy/">Debian policy</a> as bare essential minimum, but workflows beyond that are purely optional. A sponsor may have certain other requirements your package must comply to, for example some sponsors mandate a <a href="http://wiki.debian.org/debian/watch/">watch file</a>, <a href="http://dep.debian.net/deps/dep5/">DEP-5 copyright files</a>, and <a href="http://lintian.debian.org/">pedantic Lintian cleanness</a>. Have a look to those individual guidelines if applicable, before sending your mail.</p>

<h3>Technical requirements</h3>

<p>
    <dl>
    <lh>Not every sponsor likes every type of package or way to do things. Please hesitate to ask sponsors for uploading your package, if the sponsor does not explicitly allow the type of package you are trying to upload. We know about those tags:</lh>
    <dt>CDBS</dt><dd>Your package makes use of the <a href="http://build-common.alioth.debian.org/">The Common Debian Build System</a></dd>
    <dt>debhelper</dt><dd>Your package makes use of the <a href="http://kitenet.net/~joey/code/debhelper/">debhelper</a> build system</dd>
    <dt>custom debian/rules</dt><dd>Your package is using a completely customized, yet <a href="http://www.debian.org/doc/debian-policy/ch-source.html#s-debianrules">policy compliant</a> <tt>debian/rules</tt> file</dd>
    <dt>NMUs</dt><dd>Your package is a <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu">NMU</a></dd>
    <dt>QA uploads</dt><dd>Your package is a <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu-qa-upload">QA upload</a></dd>
    <dt>Backports</dt><dd>Your package is a <a href="http://backports-master.debian.org/">backported package</a></dd>
    <dt>Modified Tarballs</dt><dd>Your package modified the original source tarball somehow in a way, it does not match the original checksum anymore</dd>
    <dt>VCS snapshot tarballs</dt><dd>Your package is not based on a original source tarball at all, but is based on a VCS snapshot</dd>
    <dt>contrib/non-free packages</dt><dd>Your package it targetting the <tt>contrib</tt> or <tt>non-free</tt> branches (<a href="http://www.debian.org/doc/debian-policy/ch-archive.html#s-sections">Information</a>)</dd>
    </dl>
</p>

<h3>Social requirements</h3>

<p>Some sponsors prefer to upload only packages from people, that fulfill certain social criterias. Such examples can be, but are not limited to:</p>
<ul>
    <li>Place and time zone you are living</li>
    <li>You are willing to become a <a href="http://wiki.debian.org/DebianMaintainer">DM</a>/<a href="http://wiki.debian.org/DebianDeveloper">DD</a> some day</li>
    <li>You have packages in Debian already.</li>
    <li>Your future plans regarding Debian.</li>
</ul>
<table width="100%">
    <tr>
        <th width="10%">Sponsor name</th>
        <th width="14%">Contact data</th>
        <th width="19">Packages interested in</th>
        <th width="19%">Sponsor Guidelines</th>
        <th width="19%">Acceptable packaging styles and types</th>
        <th width="19%">Social Requirements</th>
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
        <td>${ sponsor.user.name }</td>
        <td>
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
        </td>
        <td>
            ${ sponsor.get_types() | n}
        </td>
        <td>${ sponsor.get_guidelines() | n}</td>
        <td>
            <ul>
            <% requirements = sponsor.database_to_technical_requirements() %>
            % for requirement in c.constants.SPONSOR_TECHNICAL_REQUIREMENTS:
                % if requirement[1] in requirements:
                    <li>${ requirement[0] }</li>
                % endif
            % endfor
            </ul>
        </td>
        <td>${ sponsor.get_social_requirements() | n}</td>
    </tr>
% endfor
</table>
