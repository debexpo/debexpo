<div class="qa-header">
${str(o.outcome)}
</div>
%if o.rich_data:
%if o.severity != 3:
<div class="qa-content">
%if o.severity == 2:
Upstream-Contact: was not found in d/copyright.<br/>
RFS will not autocomplete the Upstream author.
%else:
<dt>Author</dt>
<dd>${o.rich_data['upstream-author']}</dd>
%endif
<dt>License</dt>
<dd>${o.rich_data['upstream-license']}</dd>
<dt>Changelog</dt>
<dd><pre>${o.rich_data['package-changelog']}</pre></dd>
</dl>
</div>
%endif
%endif
