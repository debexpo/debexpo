${o.outcome}
%if o.rich_data["dirty"]:
Modified files:
%for filename, stat in o.rich_data["modified-files"]:
 ${filename} | ${stat}
%endfor
%endif
