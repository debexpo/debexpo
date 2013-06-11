# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('My account') }</h1>

<fieldset>
  <strong><legend>${ _('Change details') }</legend></strong>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'details') }

  <table width="100%">
    <tr>
      <td width="20%">${ _('Name') }:</td>
      <td width="80%">${ h.html.tags.text('name', value=c.user.name) }</td>
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
<hr />
<fieldset>
  <strong><legend>${ _('Change GPG key') }</legend></strong>

  ${ h.html.tags.form(h.url.current(), multipart=True) }
  ${ h.html.tags.hidden('form', 'gpg') }

  <table width="100%">

% if c.currentgpg:

    <tr>
      <td width="20%">${ _('Current GPG key') }:</td>
      <td width="80%">${ c.currentgpg }</td>
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
      <td colspan="2">Please use the output of <tt>gpg --export --export-options export-minimal --armor <i>keyid</i></tt></td>
    </tr>
    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>

   </table>

  ${ h.html.tags.end_form() }

</fieldset>
<hr />
<fieldset>
  <strong><legend>${ _('Change password') }</legend></strong>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'password') }

  <table width="100%">
    <tr>
      <td width="20%">${ _('Current password') }:</td>
      <td width="80%">${ h.html.tags.password('password_current') }</td>
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
<hr />
<fieldset>
  <strong><legend>${ _('Debian Machine Usage Policies') }</legend></strong>
  
  ${ h.html.tags.form(h.url.current(), multipart=True) }
  ${ h.html.tags.hidden('form', 'dmup') }
  % if c.current_dmup is True:
  <p>You have accepted the Debian Machine Usage Policies.</p>
  % else:

  <p>Before you can upload packages, you must accept the <a href="http://www.debian.org/devel/dmup">Debian Machine Usage Policies</a> (DMUP).</p>

  <p>Please download <a href="/my/download-dmup">this file</a>, sign it with your GPG key, and upload it:</p>

  <p>${ h.html.tags.file('signed_agreement') }</p>

  <p>${ h.html.tags.submit('commit', _('Upload')) }</p>
  % endif
  


  ${ h.html.tags.end_form() }
  
</fieldset>
<hr />
<fieldset>
  <strong><legend>${ _('Change other details') }</legend></strong>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'other_details') }

  <table width="100%">
    <tr>
      <td width="20%">${ _('Country') }:</td>
      <td width="80%">${ h.html.tags.select('country', c.current_country, sorted(c.countries.iteritems(), key=lambda x: x[1])) }</td>
    </tr>

    <tr>
      <td>${ _('IRC nickname') }:</td>
      <td>${ h.html.tags.text('ircnick', value=c.user.ircnick) }</td>
    </tr>

    <tr>
      <td>${ _('Jabber address') }:</td>
      <td>${ h.html.tags.text('jabber', value=c.user.jabber) }</td>
    </tr>

% if config['debexpo.enable_experimental_code']  == 'true':
    <tr>
        <td>${ _('Show personal data publicly') }:</td>
        <td><td>${ h.html.tags.checkbox('profile_visibility') }</td>
    </tr>
% endif

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
% if c.debian_developer and config['debexpo.enable_experimental_code']  == 'true':
  <hr />
  <fieldset>
  <strong><legend>${ _('Public sponsor info') }</legend></strong>

  ${ h.html.tags.form(h.url.current()) }
  ${ h.html.tags.hidden('form', 'metrics') }

  <table width="100%">
    <tr>
      <td width="20%">${ _('Public visibility of your profile') }:</td>
      <td width="80%">
        % for availability,label in [(c.constants.SPONSOR_METRICS_PRIVATE, _("None")), \
            (c.constants.SPONSOR_METRICS_RESTRICTED, _("Restricted")), \
            (c.constants.SPONSOR_METRICS_PUBLIC, _("Full")) ]:
            ${ h.html.tags.radio('availability', value=availability, label=label, checked=(c.metrics.availability == availability)) }
        % endfor
        <ul>
            <li><strong>None</strong> - Do not show up in the list of willing sponsors.</li>
            <li><strong>Restricted</strong> - Show only your preferred contact method publicly.</li>
            <li><strong>Full</strong> - Show full contact details publicly.</li>
        </ul>
       </td>

    <tr>
      <td>${ _('Preferred contact method for sponsored maintainer') }:</td>
      <td>${ h.html.tags.select('preferred_contact_method', c.metrics.contact, c.contact_methods)}</td>
    </tr>

    <tr>
      <td>${ _('Type of packages you are interested in') }:</td>
      <td><br />${ h.html.tags.textarea('package_types', c.metrics.types, cols=82, rows=10) }</td>
    </tr>


        <tr>
            <td>Social requirements</td>
            <td>
                <ul>
                    <li><strong>-</strong> (first column) You are not accepting packages qualifying for that tag.</li>
                    <li><strong>0</strong> (middle column) You have no strong opinion on that tag.</li>
                    <li><strong>+</strong> (last column) You endorse usage of the implied meaning of the tag.</li>
                    <li>Please note, the personal pronouns in the long description address your sponsor. Please see ${ h.tags.link_to("the sponsoring page", h.url('sponsors')) }</li>
                </ul>
            </td>
        </tr>

    % for requirement in c.social_tags:
        <tr>
            <td>&nbsp;</td>
            <td>
                <dl>
                    <dt>
                    % for weight,label in [(-1, _("-")), \
                        (0, _("0")), \
                        (1, _("+")) ]:
                        ${ h.html.tags.radio(requirement.tag, value=weight, label=label, checked=(c.metrics.get_tag_weight(requirement.tag) == weight)) }
                    % endfor
                        <span style="padding-left: 8px;">${ requirement.label }</span></dt>
                    <dd>"<em>${ requirement.long_description | n}</em>"</dd>
                    <dd>
                    </dd>
                </dl>
            </td>
        </tr>
    % endfor
    <tr>
        <td>
            ${ _("Additional social notes") }
        </td>
        <td>
        <br />${ h.html.tags.textarea('social_requirements', c.metrics.social_requirements, cols=82, rows=10) }
        </td>
    </tr>

    <tr>
        <td>Technical choices within packages</td>
        <td>
            <ul>
                <li><strong>-</strong> (first column) You are not accepting packages qualifying for that tag.</li>
                <li><strong>0</strong> (middle column) You have no strong opinion on that tag.</li>
                <li><strong>+</strong> (last column) You endorse usage of the implied meaning of the tag.</li>
                <li>Please note, the personal pronouns in the long description address your sponsor. Please see ${ h.tags.link_to("the sponsoring page", h.url('sponsors')) }</li>
            </ul>
        </td>
    </tr>
    % for requirement in c.technical_tags:
        <tr>
            <td>&nbsp;</td>
            <td>
                <dl>
                    <dt>
                    % for weight,label in [(-1, _("-")), \
                        (0, _("0")), \
                        (1, _("+")) ]:
                        ${ h.html.tags.radio(requirement.tag, value=weight, label=label, checked=(c.metrics.get_tag_weight(requirement.tag) == weight)) }
                    % endfor
                        <span style="padding-left: 8px;">${ requirement.label }</span></dt>
                    <dd>"<em>${ requirement.long_description | n}</em>"</dd>
                    <dd>
                    </dd>
                </dl>
            </td>
        </tr>
    % endfor
    <tr>
        <td>
            ${ _("Additional technical notes") }
        </td>
        <td>
        <br />
        % for guideline,label in [(c.constants.SPONSOR_GUIDELINES_TYPE_NONE, _("None")), \
            (c.constants.SPONSOR_GUIDELINES_TYPE_TEXT, _("Free text")), \
            (c.constants.SPONSOR_GUIDELINES_TYPE_URL, _("URL reference")) ]:
            ${ h.html.tags.radio('packaging_guidelines', value=guideline, label=label, checked=(c.metrics.guidelines == guideline)) }
        % endfor
        <ul>
            <li><strong>${_("None")}</strong> - You don't have any additional notes.</li>
            <li><strong>${_("Free text")}</strong> - You have additional notes you can enter below as free text.</li>
            <li><strong>${_("URL reference")}</strong> - You have your own website for sponsoring guidelines. Enter the address below.</li>
        </ul>
        <br />
        ${ h.html.tags.textarea('packaging_guideline_text', c.metrics.guidelines_text, cols=82, rows=10) }
      </td>
    </tr>

    <tr>
      <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>

  </table>
  </fieldset>

  ${ h.html.tags.end_form() }
% endif

