<div class="qa-header">
${o.outcome}
</div>
%if o.rich_data["watch-file-present"] and (not o.rich_data["watch-file-works"] or not o.rich_data["latest-upstream"]):
<div class="qa-content">
${h.converters.nl2br(o.rich_data["uscan-output"])}
</div>
%endif
