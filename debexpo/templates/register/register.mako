# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Sign up for an account') }</h1>

<fieldset>
  <legend>${ _('Account details') }</legend>

  ${ h.html.tags.form(h.url.current(), method='post') }
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
       <td>${ _('Account type') }:</td>
       <td>
         ${ h.html.tags.radio('sponsor', 0, checked=True, label='Maintainer') }
         ${ h.html.tags.radio('sponsor', 1, checked=False, label='Sponsor') }
      </td>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }

</fieldset>
