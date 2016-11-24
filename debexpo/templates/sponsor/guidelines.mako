# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>
<h1>Sponsor guidelines</h1>

To help you find a sponsor interested in your package, they can formulate sponsor traits for either social or technical aspects. Additionally a sponsor may not usually be interested in every package but only in a certain category.

<h3>Sponsor's personal interests</h3>

<p>Typically, sponsors are not interested in uploading any package for you. However, they could be interested if your package matched their area of interest. Please compare those package types with your package. Such categories eventually are certain programming languages your program is written in, a field of endeavour or software fulfilling a certain task. </p>

<%def name="tag_helper(requirement)">
    % if not c.sponsor_filter:
        <dt id="${requirement.tag}">${ requirement.label } (${ h.tags.link_to(  _('Filter'), h.url.current(action='index', t=requirement.tag))  })</dt>
        <dd>${ requirement.long_description | n}</dd>
    % elif requirement.tag not in c.sponsor_filter:
        <%
        new_tag_list = c.sponsor_filter[:]
        new_tag_list.append(requirement.tag)
        %>
        <dt><span id="${requirement.tag}" style="text-decoration: line-through;">${ requirement.label }</span> (${ h.tags.link_to(  _('Add to filter'), h.url.current(action='index', t=new_tag_list))  })</dt>
    % else:
        <%
        new_tag_list = c.sponsor_filter[:]
        new_tag_list.remove(requirement.tag)
        %>
        <dt id="${requirement.tag}">${ requirement.label } (${ h.tags.link_to(  _('Remove filter'), h.url.current(action='index', t=new_tag_list))  })</dt>
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
            Debian allows several workflows and best practices to co-exist with each other. All packages <strong>must comply to the <a href="https://www.debian.org/doc/debian-policy/">Debian policy</a></strong> as a bare essential minimum and although some workflows and best practices beyond that are optional it is nonetheless mandatory <em>for you</em> to ask someone to sponsor your upload.
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
- ${ h.tags.link_to(  _('Store filter as default'), h.url('sponsor_tag_save', t=c.sponsor_filter))  }
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
            <span style="font-size:120%"><strong>${ h.tags.link_to(sponsor.user.name, h.url(controller='sponsor', action='developer', id=sponsor.user.email)) }</strong></span>
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
