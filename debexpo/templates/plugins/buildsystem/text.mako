Buildsystem: ${o.outcome}
%if o.rich_data["build-system"] == "debhelper":
%if o.rich_data["compat-level"]:
Debhelper compatibility level ${o.rich_data["compat-level"]}
%else:
No compatibility level set!
%endif
%endif
