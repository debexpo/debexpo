<div class="qa-header">
${str(o.outcome)}
</div>
%if o.rich_data["in-debian"]:
<div class="qa-content debian-qa">
<ul>
%if o.rich_data["nmu"]:
<li>Detected as a non-maintainer upload</li>
%endif
<li>The package uploader is ${"not" if not o.rich_data["is-debian-maintainer"] else ""} currently maintaining <a href="http://packages.qa.debian.org/${o.package_version.package.name}">${o.package_version.package.name} in Debian</a></li>
%if 'latest-upload' in o.rich_data:
<li>Last upload was on the ${ o.rich_data["latest-upload"] }</li>
%endif
</ul>
</div>
%endif
