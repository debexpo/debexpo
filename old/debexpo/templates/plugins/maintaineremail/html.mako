<div class="qa-header">
${o.outcome}
</div>
%if not o.rich_data["user-is-maintainer"]:
<div class="qa-content">
<dl>
<dt>User email</dt>
<dd><a href="mailto:${o.rich_data["user-email"]}">${o.rich_data["user-email"]}</a></dd>
<dt>"Maintainer" email</dt>
<dd><a href="mailto:${o.rich_data["maintainer-email"]}">${o.rich_data["maintainer-email"]}</a></dd>
%if o.rich_data["uploader-emails"]:
<dt>"Uploaders" emails</dt>
<dd>
<ul>
%for email in o.rich_data["uploader-emails"]:
<li><a href="mailto:${email}">${email}</a></li>
%endfor
</ul>
</dd>
%endif
</dl>
</div>
%endif
