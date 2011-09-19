# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>
${ c.custom_html }

<h1>The sponsoring process</h1>

<p>As sponsored maintainer you do not have upload permissions to the Debian repository. Therefore you have three possibilities to get your package into Debian:</p>

<ul>
    <li>Join a packaging team</li>
    <li>Ask the <tt>debian-mentors</tt> mailing list</li>
    <li>Talk directly to people willing to sponsor your package</li>
</ul>

<p>A sponsor, regardless of how you found one will ${ h.tags.link_to("review", h.url('intro-reviewers')) } your package. Yet everyone is invited to review packages, including yourself. We encourage you to review other people's packages - both of you will benefit.</p>

<h2>Join a packaging team</h2>

<p>There are teams in Debian who maintain packages collaboratively. If your package deals with libraries for programming languages or is about an ecosystem of associated packages, think of KDE or Gnome packages for example, you may want to join the respective team. Have a look at the <a href="http://wiki.debian.org/Teams/#Packaging_teams">(incomplete) list of packaging teams</a> in Debian.</p>

<p>Please note, each of those teams may have their own workflows and policies covering how to deal with package uploads. Contact their respective mailing lists and home pages to learn more.</p>

<h2>Ask the <tt>debian-mentors</tt> mailing list</h2>

<p>If your package does not match the interests of any team or you are not sure whether a team could be interested in your package, please write to the <tt><a href="http://lists.debian.org/debian-mentors/">debian-mentors</a></tt> mailing list to draw attention to your package. Your request should be formatted according to our RFS ("<em>request for sponsorship</em>") template. If you uploaded your package to ${ config['debexpo.sitename'] }, a RFS template can be shown on your package page.</p>

<p><em>If you are unsure or in doubt, choose this alternative</em>.</p>

<p>Typically you will reach the greatest audience by writing to our public mailing list. Eventually also some non-uploading reviewer may have a look at your package. Please do not worry if you get no answer: It happens from time to time that all interested people might be distracted or busy. It does not mean your package is bad. Feel free to ask again after a few weeks or try any of the alternative methods to find a sponsor. </p>

<h2>Finding a sponsor</h2>

<p>If you want, you can write sponsors willing to upload packages to other maintainers directly. <em>Please do not send out mass emails!</em> Instead watch out for their individual requirements and guidelines. Contact individuals only if your package is compatible to their respective requirements and matches their area of interest. To tell apart sponsors who are interested in your package and those who are not, we asked developers to formulate their own sponsor traits. Please read them carefully and compare your package with their expectations.</p>

<h2>Sponsor metrics</h2>

To help you find a sponsor interested in your package, they can formulate sponsor traits for either social or technical aspects. Additionally a sponsor may not usually be interested in every package but only in a certain category.

<h3>Sponsor's personal interests</h3>

<p>Typically, sponsors are not interested in uploading any package for you. However, they could be interested if your package matched their area of interest. Please compare those package types with your package. Such categories eventually are certain programming languages your program is written in, a field of endeavour or software fulfilling a certain task. </p>

<%def name="tag_helper(requirement)">
    % if not c.sponsor_filter:
        <dt id="${requirement.tag}">${ requirement.label } (${ h.tags.link_to(  _('Filter'), h.url.current(action='toggle', tag=requirement.tag))  })</dt>
        <dd>${ requirement.long_description | n}</dd>
    % elif requirement.tag not in c.sponsor_filter:
        <dt><span id="${requirement.tag}" style="text-decoration: line-through;">${ requirement.label }</span> (${ h.tags.link_to(  _('Add to filter'), h.url.current(action='toggle', tag=requirement.tag))  })</dt>
    % else:
        <dt id="${requirement.tag}">${ requirement.label } (${ h.tags.link_to(  _('Remove filter'), h.url.current(action='toggle', tag=requirement.tag))  })</dt>
        <dd>${ requirement.long_description | n}</dd>
    % endif
</%def>

<table>
    <tr>
        <th width="50%">Acceptable package traits</th>
        <th width="50%">Social requirements</th>
    </tr>
    <tr>
        <td>
            Debian allows several workflows and best practices to co-exist with each other. All packages <strong>must comply to the <a href="http://www.debian.org/doc/debian-policy/">Debian policy</a></strong> as a bare essential minimum and although some workflows and best practices beyond that are optional it is nonetheless mandatory <em>for you</em> to ask someone to sponsor your upload.
        </td>
        <td>
            Some sponsors prefer to only upload packages from people who fulfill certain social criteria. Please don't ask an uploader to sponsor your request if you don't match them.
        </td>
    </tr>
    <tr>
        <td>
        <dl>
        % for requirement in c.technical_tags:
            <% tag_helper(requirement) %>
        % endfor
        </dl>
        </td>
        <td>

        <dl>
        % for requirement in c.social_tags:
            <% tag_helper(requirement) %>
        % endfor
        </dl>
        </td>
    </tr>
</table>

<hr />

<p>
% if c.sponsor_filter:
    Applied filters:
    % for filter in c.sponsor_filter:
       ${ filter }
    % endfor
- ${ h.tags.link_to(  _('Remove all filters'), h.url.current(action='clear'))  }
% endif
</p>

<table width="100%">
    <tr>
        <th width="30%">Sponsor name and contact data</th>
        <th width="35%">Acceptable package traits</th>
        <th width="35%">Social Requirements</th>
    </tr>
<%
    def preferred(flag):
        if flag:
            return "(preferred)"
        else:
            return ""

    def put_s(name):
        if name[-1] != 's':
            return 's'

    sponsors_found = False
%>
% for sponsor in c.sponsors:
    <%
        sponsor_tags = set(sponsor.get_all_tags_weighted(1))
        filters = set(c.sponsor_filter)
    %>
    % if len(filters & sponsor_tags) != len(filters):
        <% continue %>
    % endif
    <% sponsors_found = True %>
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
            <strong>Personal interests</strong>
            <p>${ sponsor.get_types() | n,semitrusted}</p>
        </td>
        <td>
            <ul>
            % for tag in sponsor.get_technical_tags_full():
                % if tag.weight > 0:
                    <li> <span style="color: green;">+ ${ tag.full_tag.label }</span> (<a href="${ h.url.current(anchor=tag.tag)  }">?</a>)</li>
                % elif tag.weight < 0:
                    <li> <span style="color: red;">- ${ tag.full_tag.label }</span> (<a href="${ h.url.current(anchor=tag.tag)  }">?</a>)</li>
                % endif
            % endfor
            </ul>
            <p>
            % if sponsor.guidelines == c.constants.SPONSOR_GUIDELINES_TYPE_URL:
                <a href="${ sponsor.get_guidelines()}">${ sponsor.user.name  }'${ put_s(sponsor.user.name) } personal guidelines</a>
            % else:
                ${ sponsor.get_guidelines() | semitrusted}
            % endif
            </p>
        </td>
        <td>
            <ul>
            % for tag in sponsor.get_social_tags_full():
                % if tag.weight > 0:
                    <li> <span style="color: green;">+ ${ tag.full_tag.label }</span> (<a href="${ h.url.current(anchor=tag.tag)  }">?</a>)</li>
                % elif tag.weight < 0:
                    <li> <span style="color: red;">- ${ tag.full_tag.label }</span> (<a href="${ h.url.current(anchor=tag.tag)  }">?</a>)</li>
                % endif
            % endfor
            </ul>
            ${ sponsor.get_social_requirements() | n,semitrusted}
        </td>
    </tr>
% endfor
%if not sponsors_found and c.sponsor_filter:
    <tr>
        <td colspan="3" style="text-align:center"><br /><strong>${ _('No sponsor matched your criteria') }</strong></td>
    </tr>
%elif not sponsors_found:
    <tr>
        <td colspan="3" style="text-align:center"><br /><strong>${ _('No sponsors found') }</strong></td>
    </tr>
%endif
</table>

% if c.sponsor_filter:
    <p>${ h.tags.link_to(  _('Remove all filters'), h.url.current(action='clear'))  }</p>
% endif
