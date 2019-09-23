# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<%include file="/user.mako"/>
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

<h2>Sponsoring Guidelines</h2>

<h3>Personal interests</h3>
<p>${ c.sponsor.get_types() | n,semitrusted}</p>


<table width="100%">
<tr>
    <td width="50%"><h3>Acceptable package traits</h3></td>
    <td width="50%"><h3>Social Requirements</h3></td>
</tr>
<tr>
    <td>
    <ul>
    % for tag in c.sponsor.get_technical_tags_full():
        % if tag.weight != 0:
            <li>
            % if tag.weight > 0:
                <span style="color: green;">+
            % elif tag.weight < 0:
                <span style="color: red;">-
            % endif
                ${ tag.full_tag.label }</span>: ${ tag.full_tag.long_description | n}
            </li>
        % endif
    %endfor
    </ul>

    <p>
        % if c.sponsor.guidelines == c.constants.SPONSOR_GUIDELINES_TYPE_URL:
            <a href="${ sponsor.get_guidelines()}">${ c.sponsor.user.name  }'${ put_s(c.sponsor.user.name) } personal guidelines</a>
        % else:
            ${ c.sponsor.get_guidelines() | semitrusted}
        % endif
    </p>
    </td>
    <td>

    <ul>
    % for tag in c.sponsor.get_social_tags_full():
        % if tag.weight != 0:
            <li>
            % if tag.weight > 0:
                <span style="color: green;">+
            % elif tag.weight < 0:
                <span style="color: red;">-
            % endif
                ${ tag.full_tag.label }</span>: ${ tag.full_tag.long_description | n}
            </li>
        % endif
    % endfor
    </ul>

    <p>${ c.sponsor.get_social_requirements() | n,semitrusted}</p>
    </td>
</tr>
</table>
