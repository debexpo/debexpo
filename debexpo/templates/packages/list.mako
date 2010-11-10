# -*- coding: utf-8 -*-

<table width="100%">
  <tr>
    <th>${ _('Package') }</th>
    <th>${ _('Description') }</th>
    <th>${ _('Version') }</th>
    <th>${ _('Uploader') }</th>
    <th>${ _('Needs a sponsor') }?</th>
  </tr>

% if len(c.packages) > 0:

    % for package in c.packages:
      <tr>
        <td class="lines"><a href="${ h.url('package', packagename=package.name) }">${ package.name }</a></td>
        <td class="lines">${ package.description.replace('\n', '<br/>') }</td>
        <td class="lines">${ package.package_versions[-1].version }</td>
        <td class="lines"><a href="${ h.url('packages-uploader', id=package.user.email) }">${ package.user.name }</a></td>
        <td class="lines">
    % if package.needs_sponsor:
                ${ _('Yes') }
    % else:
                ${ _('No') }
    % endif
        </td>
      </tr>
    % endfor

% else:

    <tr>
      <td class="lines" colspan="5" align="center">${ _('No packages') }</td>
    </tr>

% endif

</table>
