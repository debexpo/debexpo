# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

${ c.custom_html }

<h1>Introduction for sponsors</h1>

<h3>What is a sponsor?</h3>

<p>Someone who uploads the package and is responsible for the package in the archive. The sponsor is responsible for the quality of the package and checks the work of the package maintainer to improve his skills.</p>

<h3>Motivation</h3>

<p>Thanks for helping. There are a lot of sponsorees waiting for a Developer to help them with their packages, and if you want to help with the New Maintainer process this is a good step to get involved.</p>

<h3>What to do for sponsoring</h3>

<p>Look for packages that you would like to sponsor on this website. Once you have found some you should download, build and test them. Please notify your sponsoree of every problem that you find in order to give him a chance to fix them. We believe that it is of uttermost importance to stay in contact with your sponsorees to keep them interested in working on Debian. Moreover, they will also learn how to maintain packages within a team and will learn skills that are crucial for Debian Developers more easily. </p>

<table width="100%">
    <tr>
        <th width="20%">Sponsor name</th>
        <th width="20%">Contact data</th>
        <th width="20%">Sponsor Guidelines</th>
        <th width="20%">Technical Requirements</th>
        <th width="20%">Social Requirements</th>
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
