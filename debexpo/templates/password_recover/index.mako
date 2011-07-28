# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Password recovery')}</h1>

  ${ h.html.tags.form(h.url.current(), method='post') }

  <p>If you forgot your password, here is what we can do for you.</p>

  <ol>
    <li>You should fill out this form.</li>
    <li>You will get an email with a link. Click the link.</li>
    <li>Then the web app will change your password to something random. Please log in with that password and change it.</li>
  </ol>

  <p>Not super hard. If you're ready, I'm ready.</p>

% if c.message:
  <p><span class="error-message">${ c.message }</span></p>
% endif

  <table>
    <tr>
      <td>${ _('Your email address') }:</td>
      <td>${ h.html.tags.text('email') }</td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
  </table>

  ${ h.html.tags.end_form() }


</table>
