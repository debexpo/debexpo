# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('My account') }</h1>

<fieldset>
  <legend>${ _('Change details') }</legend>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'details') }

  <table>
    <tr>
      <td>${ _('Name') }:</td>
      <td>${ h.html.tags.text('name', value=c.user.name) }</td>
    </tr>

    <tr>
      <td>${ _('E-mail') }:</td>
      <td>${ h.html.tags.text('email', value=c.user.email) }</td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }

</fieldset>

<fieldset>
  <legend>${ _('Change GPG key') }</legend>

  ${ h.html.tags.form(h.url.current(), multipart=True) }
  ${ h.html.tags.hidden('form', 'gpg') }

  <table>

% if c.currentgpg:

    <tr>
      <td>${ _('Current GPG key') }:</td>
      <td>${ c.currentgpg }</td>
    </tr>

    <tr>
      <td>${ _('Delete current key') }:</td>
      <td>${ h.html.tags.checkbox('delete_gpg') }</td>
    </tr>

% else:

    ${ h.html.tags.hidden('delete_gpg', 0) }

% endif

    <tr>
      <td>${ _('GPG key') }:</td>
      <td>${ h.html.tags.file('gpg') }</td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>

   </table>

  ${ h.html.tags.end_form() }

</fieldset>

<fieldset>
  <legend>${ _('Change password') }</legend>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'password') }

  <table>
    <tr>
      <td>${ _('Current password') }:</td>
      <td>${ h.html.tags.password('password_current') }</td>
    </tr>

    <tr>
      <td>${ _('New password') }:</td>
      <td>${ h.html.tags.password('password_new') }</td>
    </tr>

    <tr>
      <td>${ _('Confirm new password') }:</td>
      <td>${ h.html.tags.password('password_confirm') }</td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }

</fieldset>

<fieldset>
  <legend>${ _('Change other details') }</legend>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'other_details') }

  <table>
    <tr>
      <td>${ _('Country') }:</td>
      <td>${ h.html.tags.select('country', c.current_country, c.countries) }</td>
    </tr>

    <tr>
      <td>${ _('IRC nickname') }:</td>
      <td>${ h.html.tags.text('ircnick', value=c.user.ircnick) }</td>
    </tr>

    <tr>
      <td>${ _('Jabber address') }:</td>
      <td>${ h.html.tags.text('jabber', value=c.user.jabber) }</td>
    </tr>

% if c.config['debexpo.debian_specific'] == 'true':

    % if c.debian_developer:

        <tr>
          <td>${ _('Debian status') }:</td>
          <td>${ _('Debian Developer') }</td>
        </tr>
	${ h.html.tags.hidden('status') }

    % else:

        <tr>
          <td><a href="http://wiki.debian.org/Maintainers">${ _('Debian Maintainer') }</a>:</td>
          <td>${ h.html.tags.checkbox('status', checked=c.debian_maintainer) }</td>
        </tr>

    % endif

% else:

    ${ h.html.tags.hidden('status') }

% endif

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }

</fieldset>
