${o.outcome}
%if o.rich_data["watch-file-present"] and (not o.rich_data["watch-file-works"] or not data["latest-upstream"]):
Uscan output :
${o.rich_data["uscan-output"]}
%endif
