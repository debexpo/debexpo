<div class="qa-header">
${str(o.outcome)}
</div>
%if o.rich_data["dirty"]:
<div class="qa-content">
<table>
<th><td>Modified file</td><td>diffstat</td></th>
%for filename, stat in o.rich_data["modified-files"]:
<tr><td>${filename}</td><td>${stat}</td></tr>
%endfor
</table>
</div>
%endif
