<%doc>
    This needs to be re-implemented into something truly recursive. Feel free to do
    if you find yourself in the need to add 3 layered sub menus
</%doc>
<div id="second-nav">
    % if c.submenu.has_label():
    <p>${ c.submenu.label() }</p>
    % endif

    <ul>
    % for label,link in c.submenu.entries():
        <li>${ h.tags.link_to(label, h.url(link)) }</li>
    % endfor

    % if c.submenu.has_submenu():
    <li>${ c.submenu.submenulabel() }</li>
    <ul>
    % for menus in c.submenu.menus():
        % for label,link in menus.entries():
            <li>${ h.tags.link_to(label, h.url(link)) }</li>
        % endfor
    % endfor
    </ul>
    % endif
    </ul>
</div> <!-- end second-nav -->
