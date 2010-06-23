# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Login') }</h1>

<fieldset>
  <legend>${ _('Login') }</legend>

  <p>${ _('Please login to continue') }</p>

% if c.message:
  <p><span class="error-message">${ c.message }</span></p>
% endif

  ${ h.html.tags.form(h.url.current(), method='post') }

  <table>
    <tr>
      <td>${ _('E-mail') }:</td>
      <td>${ h.html.tags.text('email') }</td>
    </tr>

    <tr>
      <td>${ _('Password') }:</td>
      <td>${ h.html.tags.password('password') }</td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }

</fieldset>
