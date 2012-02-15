<div class="qa-header">
${str(o.outcome)}
</div>
%if o.rich_data:
<div class="qa-content">
<dl>
%for field, contents in sorted(o.rich_data.items()):
<dt>${field}</dt>
<dd><a href="${contents}">${contents}</a></dt>
%endfor
</dl>
</div>
%endif
