# -*- coding: utf-8 -*-
Package: sponsorship-requests
%if c.severity:
Severity: ${ c.severity }
%else:
Severity: normal [important for RC bugs, wishlist for new packages]
%endif

Dear mentors,

%if c.package:
I am looking for a sponsor for my package "${ c.package.name }"
%else:
I am looking for a sponsor for my package "hello":
%endif

%if c.package:
 * Package name    : ${ c.package.name }
   Version         : ${ c.package.package_versions[-1].version }
%else:
 * Package name    : hello
   Version         : 3.1-4
%endif
%if c.rfstemplate:
   Upstream Author : ${ c.rfstemplate['upstream-author'] }
%if 'upstream-url' in c.rfstemplate:
 * URL             : ${ c.rfstemplate['upstream-url'] }
%else:
 * URL             : [fill in URL of upstream's web site]
%endif
 * License         : ${ c.rfstemplate['upstream-license'] }
%if 'package-vcs' in c.rfstemplate:
 * Vcs             : ${ c.rfstemplate['package-vcs'] }
%else:
 * Vcs             : None
%endif
%else:
   Upstream Author : [fill in name and email of upstream]
 * URL             : [fill in URL of upstream's web site]
 * License         : [fill in]
 * Vcs             : [fill in URL of packaging vcs]
%endif
%if c.package:
   Section         : ${ c.package.package_versions[-1].section }
%else:
   Section         : [fill in]
%endif

It builds those binary packages:

%if c.package and c.package.description:
  ${ '\n  '.join(c.package.description.splitlines()) }
%else:
  hello - friendly greeter
%endif

To access further information about this package, please visit the following URL:

%if c.package:
  ${ c.config['debexpo.server'] }${ h.url('package', packagename=c.package.name) }
%else:
  ${ c.config['debexpo.server'] }/package/hello
%endif

Alternatively, one can download the package with dget using this command:

%if c.package:
% for pkgfile in c.package.package_versions[-1].source_packages[0].package_files:
  % if pkgfile.filename.endswith('.dsc'):
  dget -x ${ c.config['debexpo.server'] }/debian/${ pkgfile.filename }
  % endif
% endfor
%else:
  dget -x ${ c.config['debexpo.server'] }/debian/pool/main/h/hello/hello_3.1-4.dsc
%endif

Changes since the last upload:

%if c.rfstemplate:
${ c.rfstemplate['package-changelog'] }
%else:
[your most recent changelog entry]
%endif

Regards,
