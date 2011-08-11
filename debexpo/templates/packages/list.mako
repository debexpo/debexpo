# -*- coding: utf-8 -*-

% for packagegroup in c.deltas:
        <h2>${ packagegroup.label }</h2>

        <table width="100%">
          <tr>
            <th width="15%">${ _('Package') }</th>
            <th width="50%">${ _('Description') }</th>
            <th width="10%">${ _('Version') }</th>
            <th width="15%">${ _('Uploader') }</th>
            <th width="10%">${ _('Needs a sponsor') }?</th>
          </tr>

        % if len(packagegroup.packages) > 0:
                % for package in packagegroup.packages:
                      <tr>
                        <td class="lines"><a href="${ h.url('package', packagename=package.name) }">${ package.name }</a></td>
                        <td class="lines">${ package.get_description_nl2br() | n }</td>
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
% endfor
