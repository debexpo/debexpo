<div class="qa-header">
${o.from_plugin}: ${str(o.outcome)}
</div>
%if o.rich_data:
<div class="qa-content">
${h.converters.nl2br(str(o.rich_data))}
</div>
%endif
