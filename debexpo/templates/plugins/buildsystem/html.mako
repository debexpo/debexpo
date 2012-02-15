<div class="qa-header">
Buildsystem: ${o.outcome}
</div>
<div class="qa-content">
%if o.rich_data["build-system"] == "debhelper":
%if o.rich_data["compat-level"]:
Debhelper compatibility level ${o.rich_data["compat-level"]}
%else:
No compatibility level set!
%endif
%endif
</div>