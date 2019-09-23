% if o.rich_data:
%   for package in o.rich_data:
%     for severity in o.rich_data[package]:
%       for tag in sorted(o.rich_data[package][severity]):
%         if any(o.rich_data[package][severity][tag]):
%           for data in o.rich_data[package][severity][tag]:
${severity}: ${package}: ${tag} ${" ".join(data)}
%           endfor
%         endif
%       endfor
%     endfor
%   endfor
% endif
