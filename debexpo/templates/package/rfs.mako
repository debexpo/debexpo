# -*- coding: utf-8 -*-
<%inherit file="../base.mako"/>

<h1>${ _('Template for an RFS for "%s"') % c.package.name }</h1>

<p>An RFS is a <i>request for sponsorship</i>. If you want to show other people
that you are looking for a sponsor for your package you can file a bug against
the sponsorship-request pseudo-package containing information about your
package. See our ${ h.tags.link_to("RFS procedure page", h.url('rfs-howto')) } for details.</p>

<p><strong>Note</strong>: You might not get a reply to your request if you do not
subscribe to the debian-mentors mailing list. You can <a href="http://lists.debian.org/debian-mentors">
subscribe to the mailing list by clicking here</a> and following the simple steps to confirm
your subscription request. It can also take time for sponsors to look over the requests, so
please do not give up quickly and keep a watch over the mailing list.</p>



<pre>
From: ${ c.package.user.name } &lt;${ c.package.user.email }&gt
To: submit@bugs.debian.org
Subject: RFS: ${ c.package.name } [[put in NEW, RC, NMU if applicable]]


Package: sponsorhip-requests
Severity: wishlist [change to important for RC bugs, normal for follow-up uploads]

Dear mentors,

I am looking for a sponsor for my package "${ c.package.name }".

 * Package name    : ${ c.package.name }
   Version         : ${ c.package.package_versions[-1].version }
   Upstream Author : [fill in name and email of upstream]
 * URL             : [fill in URL of upstreams web site]
 * License         : [fill in]
   Section         : ${ c.package.package_versions[-1].section }

It builds those binary packages:

${ c.package.description }

To access further information about this package, please visit the following URL:

  ${ c.config['debexpo.server'] }${ h.url('package', packagename=c.package.name) }

Alternatively, one can download the package with dget using this command:

% for pkgfile in c.package.package_versions[-1].source_packages[0].package_files:
    % if pkgfile.filename.endswith('.dsc'):
  dget -x ${ c.config['debexpo.server'] }/debian/${ pkgfile.filename }
    % endif
% endfor

[your most recent changelog entry]

I would be glad if someone uploaded this package for me.

Kind regards,

${ c.package.user.name }
</pre>
