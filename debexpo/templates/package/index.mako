# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Details about package "%s"') % c.package.name }</h1>

<table>
  <tr>
    <th>${ _('Name') }:</th>
    <td>${ c.package.name }

% for pkginfo in c.package.package_versions[0].package_info:
    % if pkginfo.data == 'Package is in Debian':

        (<a href="http://packages.qa.debian.org/?src=${ c.package.name | u }">PTS</a>)

    % endif
% endfor

    </td>
  </tr>

  <tr>
    <th>${ _('Uploader') }:</th>
    <td><a href="${h.url('packages-uploader', id=c.package.user.email) }">${ c.package.user.name }</a> &lt;<a href="mailto:${c.package.user.email }">${ c.package.user.email }</a>&gt;

% if c.config['debexpo.debian_specific'] == 'true':

    (<a href="http://qa.debian.org/developer.php?login=${c.package.user.email | u }">Debian QA page</a>)

% endif

    </td>
  </tr>

  <tr>
    <th>${ _('Description') }:</th>
    <td>${ c.package.get_description() | semitrusted}</td>
  </tr>

% if 'user_id' in c.session:

  <tr>
    <th>${ _('Subscribe') }:</th>
    <td><a href="${h.url('subscribe', packagename=c.package.name)}">${ _('Edit your subscription') }</a></td>
  </tr>


  <tr>
  <th>${ _('Needs a sponsor') }:</th>
  <td>
    % if c.package.needs_sponsor:
                ${  _('Yes')  }
    % else:
                ${ _('No')  }
  % endif
  % if 'user_id' in c.session and c.session['user_id'] == c.package.user_id:
    (${ h.tags.link_to(  _('Change'), h.url('sponsor', packagename=c.package.name, key=c.user.get_upload_key()))  })
  % endif
  </td>
  </tr>

% endif

% if 'user_id' in c.session and c.session['user_id'] == c.package.user_id:

  <tr>
    <th>${ _('Delete package') }:</th>
    <td>${ h.html.tags.link_to(_('Delete this package'), h.url.current(action="delete", packagename=c.package.name, key=c.user.get_upload_key()), confirm=_('Are you sure?')) }</td>
  </tr>

% endif

</table>

<h1>${ _('Package versions') }</h1>

% for package_version in sorted(c.package.package_versions, key=lambda pv: pv.uploaded, reverse=True):

  <h2>Version ${ package_version.version }</h2>

  <h3>${ _('Information')}</h3>

  <table>
    <tr class="pkg-list">
      <th>${ _('Version') }:</th>
      <td>${ package_version.version }

% if c.config['debexpo.debian_specific'] == 'true' and c.session.get('user_id') == c.package.user_id:

  (<a href="${ h.url('rfs', packagename=c.package.name) }">${ _('View RFS template') }</a>)

% endif

      </td>
    </tr>

    <tr class="pkg-list">
      <th>${ _('Uploaded') }:</th>
      <td>${ package_version.uploaded.strftime("%Y-%m-%d %H:%M %Z")}</td>
    </tr>

    <tr>
      <th>${ _('Source package') }:</th>
      <td>

    % for pkgfile in package_version.source_packages[0].package_files:

        % if pkgfile.filename.endswith('.dsc'):

            <a href="${ c.config['debexpo.server'] }/debian/${ pkgfile.filename }">${ c.config['debexpo.server'] }/debian/${ pkgfile.filename }</a>

        % endif

    % endfor

      </td>
    </tr>

    <tr class="pkg-list">
      <th>${ _('Section') }:</th>
      <td>${ package_version.section }</td>
    </tr>

    <tr class="pkg-list">
      <th>${ _('Priority') }:</th>
      <td>${ package_version.priority }</td>
    </tr>

% if c.config['debexpo.debian_specific'] == 'true':

    % if package_version.closes is not None:

    <tr class="pkg-list">
      <th>${ _('Closes bugs') }:</th>
      <td>

        % for bug in package_version.closes.split():

      <a href="http://bugs.debian.org/${ bug }">${ bug }</a>

        % endfor
      </td>
    </tr>

    % endif

% endif
</table>

% if package_version.package_info:
<h3>${ _('QA information')}</h3>

<table>

    ## Print result from plugins
    % for pkginfo in package_version.package_info:
        % if pkginfo.data:
            <tr class="pkg-list">
                <th>${ h.constants.PLUGIN_SEVERITY[pkginfo.severity] }:</th>
                <td>${ h.converters.nl2br(pkginfo.data) }</td>
            </tr>
        % endif
    % endfor
</table>
% endif

<h3>Comments</h3>

% if len(package_version.package_comments) > 0:

  <ol>

  % for comment in package_version.package_comments:

    <li>
      <p>
        <pre>${ h.util.html_escape(comment.text) }</pre>

% if comment.outcome == c.constants.PACKAGE_COMMENT_OUTCOME_NEEDS_WORK:

  <span style="color: red;">${ _('Needs work') }</span>

% elif comment.outcome == c.constants.PACKAGE_COMMENT_OUTCOME_PERFECT:

  <span style="color: green;">${ _('Perfect') }</span>

% endif

        <i>${ comment.user.name } at ${ comment.time }</i>

% if comment.status == c.constants.PACKAGE_COMMENT_STATUS_UPLOADED and c.config['debexpo.debian_specific'] == 'true':

  <strong>${ _('Package has been uploaded to Debian') }</strong>

% endif

     </p>
   </li>

  % endfor

  </ol>

% else:

<p><i>${ _('No comments') }</i></p>

% endif

% if 'user_id' in c.session:
<h4>New comment</h4>
<fieldset>
${ h.html.tags.form(h.url('comment', packagename=c.package.name), method='post') }
${ h.html.tags.hidden('package_version', package_version.id) }

% if hasattr(c, 'form_errors'):
    <% c.form_errors %>
% endif

<table>
    <tr>
        <td>Comment</td>
        <td>${ h.html.tags.textarea('text', cols=82, rows=10) }</td>
    </tr>
    <tr>
        <td>Outcome</td>
        <td>${ h.html.tags.select('outcome', c.constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED, c.outcomes) }</td>
    </tr>
% if config['debexpo.debian_specific'] == 'true' and c.user.status == c.constants.USER_STATUS_DEVELOPER:
    <tr>
        <td>${ _('Uploaded to Debian') }</td>
        <td>${ h.html.tags.checkbox('status') }</td>
    </tr>
% endif
    <tr>
        <td>${ h.html.tags.submit('commit', _('Submit')) }</td>
    </tr>
</table>
${ h.html.tags.end_form() }

</fieldset>

% endif

% endfor
