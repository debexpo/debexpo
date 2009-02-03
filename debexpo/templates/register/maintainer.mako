# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Sign up for a maintainer account') }</h1>

<fieldset>
  <legend>${ _('Account details') }</legend>

  ${ h.html.tags.form(h.url_for(), method='post') }

  <table>
    <tr>
      <td>${ _('Full name') }:</td>
      <td>${ h.html.tags.text('name') }</td>
    </tr>

    <tr>
      <td>${ _('E-mail') }:</td>
      <td>${ h.html.tags.text('email') }</td>
    </tr>

    <tr>
      <td>${ _('Password') }:</td>
      <td>${ h.html.tags.password('password') }</td>
    </tr>

    <tr>
      <td>${ _('Confirm password') }:</td>
      <td>${ h.html.tags.password('password_confirm') }</td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }

</fieldset>
