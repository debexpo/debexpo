<h1>${ c.profile.name }</h1>
<h3>
% if c.profile.status == c.constants.USER_STATUS_DEVELOPER:
    ${ _('Debian Developer') }
% elif c.profile.status == c.constants.USER_STATUS_MAINTAINER:
    ${ _('Debian Maintainer') }
% else:
    ${ _('Maintainer') }
% endif
</h3>

<h2>User Information</h2>

<table width="100%">
    <tr>
        <td width="50%">
            <dl>
                <dt>Email:</dt>
                <dd>${ c.profile.email }</dd>
                <dt>IRC:</dt>
                <dd>${ c.profile.ircnick }</dd>
                <dt>Jabber:</dt>
                <dd>${ c.profile.jabber }</dd>
            </dl>
        </td>
        <td width="50%">
            <dl>
                <dt>Country</dt>
                <dd>
                % if c.profile.country_id != None:
                    ${ c.countries[c.profile.country_id] }
                % else:
                    ${ _('Not specified') }
                % endif
                </dd>
                <dt>GnuPG</dt>
                <dd>${ c.profile.gpg_id }</dd>
            </dl>
        </td>
    </tr>
</table>

