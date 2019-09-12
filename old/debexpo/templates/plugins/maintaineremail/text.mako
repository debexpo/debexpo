${o.outcome}
%if not o.rich_data["user-is-maintainer"]:
 - User email: ${o.rich_data["user-email"]}
 - "Maintainer" email: ${o.rich_data["maintainer-email"]}
%if o.rich_data["uploader-emails"]:
 - "Uploaders" emails:
%for email in o.rich_data["uploader-emails"]:
    - ${email}
%endfor
%endif
%endif
