${o.outcome}
%if o.rich_data["errors"]:
Errors:
%  for error in o.rich_data["errors"]:
 - ${error}
%  endfor
%endif
%for package in o.rich_data["bugs"]:
Bugs closed in ${package}:
%for bugnum, title, severity in o.rich_data["bugs"][package]:
 - #${bugnum} (${severity}): ${title}
%endfor
%endfor
