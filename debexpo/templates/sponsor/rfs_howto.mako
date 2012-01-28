# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>The sponsorship process</h1>

<p>In general all mails should be sent to the RFS request
(<em>nnn@bugs.debian.org</em>). Please also Cc the submitter
(<em>nnn-submitter@bugs.debian.org</em>). A copy will be sent to the mailing list
automatically by the bug tracker.</p>

<h2>Asking for Sponsorship</h2>

<p>An RFS is a <i>request for sponsorship</i>. If you want to show other people
that you are looking for a sponsor for your package you can file a bug against
the sponsorship-request pseudo-package containing information about your
package. See our ${ h.tags.link_to("RFS procedure page", h.url('rfs-howto')) } for details.</p>

<p><strong>Note</strong>: You might not get a reply to your request if you do not
subscribe to the debian-mentors mailing list or to your sponsoring-requests
bug. You can <a href="http://lists.debian.org/debian-mentors"> subscribe to the
mailing list by clicking here</a> and following the simple steps to confirm
your subscription request. It can also take time for sponsors to look over the requests, so
please do not give up quickly and keep a watch over the mailing list.</p>


<p>Once a source package has been prepared and made available (for example by
uploading it to this site) file a new bug report against the <a href="http://bugs.debian.org/cgi-bin/pkgreport.cgi?pkg=sponsorship-requests"><strong><em>sponsorhip-requests</em></strong></a>
pseudo-package.</p>


<h2>
%if c.package:
    ${ _('Template for an RFS for "%s"') % c.package.name }
%else:
    ${ _('Template for an RFS bug') }
%endif
</h2>

<pre>
%if c.package:
  From: ${ c.package.user.name } &lt;${ c.package.user.email }&gt
%else:
  From: J. Maintainer &lt;j@example.com&gt;
%endif
  To: submit@bugs.debian.org
%if c.package:
  Subject: RFS: ${ c.package.name }/${ c.package.package_versions[-1].version } [put in NEW, RC, NMU if applicable]
%else:
  Subject: RFS: hello/3.1-4 -- friendly greeter [put in NEW, RC, NMU if applicable]
%endif



  Package: sponsorhip-requests
  Severity: normal [important for RC bugs, wishlist for new packages]

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
   Upstream Author : [fill in name and email of upstream]
 * URL             : [fill in URL of upstreams web site]
 * License         : [fill in]
%if c.package:
   Section         : ${ c.package.package_versions[-1].section }
%else:
   Section         : [fill in]
%endif

  It builds those binary packages:

%if c.package:
    ${ c.package.description }
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

  More information about hello can be obtained from http://www.example.com.

  Changes since the last upload:

  [your most recent changelog entry]

  hello (3.1-4) unstable; urgency=low


  Regards,
%if c.package:
   ${ c.package.user.name }
%else:
  J. Maintainer
%endif
</pre>

<p>Please indicate in the subject if the package fixes RC bugs, is a QA or
NMU upload or a new package:</p>

<pre>
  Subject: RFS: hello/1.0-1 [NEW] -- friendly greeter
  Subject: RFS: hello/1.0-3 [QA] -- friendly greeter
  Subject: RFS: hello/1.0-1.1 [NMU] [RC] -- friendly greeter
  Subject: RFS: hello/1.0-2 [RC] -- friendly greeter
</pre>

The meaning of this shortcuts is denoted below, in case you are unsure:

<dl>
    <dt>NEW</dt>
        <dd>The package does not exist in Debian yet. It needs to go through NEW. That is the <a href="http://ftp-master.debian.org/new.html">queue on ftp-master</a> for packages uploaded for the first time, which need to be reviewed first. This includes renames, packages moving between areas, and source-packages that build new binary packages.</dd>
    <dt>QA</dt>
        <dd>You upload is a QA upload. Please refer to the respective section in the <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu-qa-upload">developer's reference</a> to learn about QA uploads.</dd>
    <dt>NMU</dt>
        <dd>This short for "Non-Maintainer Upload"; a version of a package that is not uploaded by the official Maintainer of a package, but rather by you. For NMUs special rules apply. Please see the <a href="http://www.debian.org/doc/manuals/developers-reference/pkgs.html#nmu">developer's reference</a> again.</dd>
    <dt>RC</dt>
        <dd>This is short for "Release-Critical". That is a class of bugs which are particularly important. Use this indication if your request fixes such RC-bugs.</dd>
</dl>

<p>Please keep track of the bug and respond to comments. If the bug was
tagged moreinfo or wontfix and you think you have addressed the issues,
please remove the respective tag again.</p>

<p>If you changed the package to address concerns, please send a follow-up
to the sponsoring request (To: <em>nnn@bugs.debian.org</em>) that includes the
URL to the source package and the last changelog entries similar to the
initial request.</p>

<p>If there are issues with the upload after the bug was closed, for
example when the package was rejected by the archive software, you can
reopen the bug (again, please include references to the updated source
package or ask for advice).</p>


<h2>Reviewing Packages</h2>

<p>Anybody feeling competent enough is invited to review sponsoring
requests. You do not need to be a Debian Developer to do so.</p>

<p>Please send any comments to <em>nnn@bugs.debian.org</em> (Cc:
<em>nnn-submitter@bugs.debian.org</em>). You can use the following tags to indicate
progress:</p>


<dl>
 <dt>moreinfo</dt>
    <dd>open questions or changes are required before an upload. The package needs work before it can be uploaded.</dd>
 <dt>confirmed</dt>
    <dd>somebody did a brief review the package and it looks sane. It can still have (smaller) issues that need to be fixed before an upload.</dd>
 <dt>pending</dt>
    <dd>somebody is willing to look after the package until it is uploaded.<dd>
 <dt>wontfix</dt>
    <dd>large problems or cannot not be uploaded at all.</dd>
</dl>


<p>If you intend to take care of the sponsoring request until the package
is ready for upload, please consider setting yourself as the owner of
the bug and tag the bug pending:</p>

<code>
  $ bts owner nnn me@example.com , tag it + pending
</code>

<h2>Uploading Packages</h2>

<p>After you uploaded a package, please close the bug report by sending a
mail to <em>nnn-done@bugs.debian.org</em>. Do not close RFS bugs in
debian/changelog. It is the sponsor who solves the issue, not the
supplier of the package or anyhow related to the package itself.</p>

<h2>Notes</h2>

<p>Inactive requests should be closed (semi-)automatically after a longer
term of no activity (two weeks for requests tagged wontfix, six weeks
for requests tagged moreinfo and six months for others). The same
applies to uploaded packages for which the sponsor forgot to close the
RFS bug.</p>

