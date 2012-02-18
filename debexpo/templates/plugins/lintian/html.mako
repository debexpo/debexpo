<%!
def decode_severity(s):
    """Decode a lintian severity"""
    verbose_severity = {
      'E': 'Error',
      'W': 'Warning',
      'P': 'Pedantic',
      'I': 'Info',
      'O': 'Override',
      'X': 'Experimental',
    }.get(s, '???')

    return '''<span class="lintian-%(s)s" title="%(verbose_severity)s">%(s)s</span>''' % locals()

def tag_to_a(tag):
    """Return a link to the lintian tag description"""
    return '<a href="http://lintian.debian.org/tags/%s.html">%s</a>' % (tag, tag)

def severity_key(x):
    """Key to sort lintian severities"""
    return "EWIPOX".index(x)
%>
<div class="qa-header">
${o.outcome}
</div>
% if o.rich_data:
<div class="qa-content">
%   for package in o.rich_data:
<div class="lintian-pkgname">
${package}
</div>
<ul class="lintian-contents">
%     for severity in sorted(o.rich_data[package], key = severity_key):
%       for tag in sorted(o.rich_data[package][severity]):
<li>
${decode_severity(severity)} ${tag_to_a(tag)}
%         if any(o.rich_data[package][severity][tag]):
<ul>
%           for data in o.rich_data[package][severity][tag]:
<li>${" ".join(data) | h}</li>
%           endfor
</ul>
%         endif
</li>
%       endfor
%     endfor
</ul>
%   endfor
</div>
% endif
